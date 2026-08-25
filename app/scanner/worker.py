from PySide6.QtCore import QThread, Signal
from datetime import datetime
import time
from typing import List

from app.models.device import DeviceInfo
from app.models.port import PortInfo
from app.models.session import ScanSession
from app.scanner.arp_scanner import NetworkDiscoveryEngine
from app.scanner.port_scanner import PortScannerEngine
from app.scanner.os_detector import OSDetector
from app.core.config import AppConfig
from app.core.logger import logger


class DiscoveryScanWorker(QThread):
    progress_changed = Signal(int, int, str)
    host_discovered = Signal(object)
    scan_finished = Signal(object)
    scan_failed = Signal(str)

    def __init__(self, target_range: str, scan_type: str = "Quick Scan", timeout: float = 1.0, threads: int = 100):
        super().__init__()
        self.target_range = target_range
        self.scan_type = scan_type
        self.timeout = timeout
        self.threads = threads
        self.engine = NetworkDiscoveryEngine(timeout=timeout, max_threads=threads)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        self.engine.cancel()

    def run(self):
        t0 = time.time()
        start_dt = datetime.now()
        session = ScanSession(
            scan_type=self.scan_type,
            target_range=self.target_range,
            start_time=start_dt
        )

        try:
            def on_progress(current, total, ip):
                self.progress_changed.emit(current, total, ip)

            def on_host(dev: DeviceInfo):
                self.host_discovered.emit(dev)

            devices = self.engine.scan(
                self.target_range,
                progress_callback=on_progress,
                host_found_callback=on_host
            )

            if self.scan_type == "Full Scan" and not self._is_cancelled:
                port_engine = PortScannerEngine(timeout=0.3, max_threads=50)
                preset_ports = AppConfig.PORT_PRESETS["Quick (Top 20)"]
                total_open = 0

                for dev in devices:
                    if self._is_cancelled:
                        break
                    ports = port_engine.scan_ports(dev.ip, preset_ports)
                    dev.open_ports = ports
                    total_open += len(ports)
                    banners = [p.banner for p in ports if p.banner]
                    dev.os_detected = OSDetector.refine_os_from_banners(banners, dev.os_detected)

                session.total_open_ports = total_open

            session.devices = devices
            session.total_hosts_found = len(devices)
            session.end_time = datetime.now()
            session.duration_seconds = time.time() - t0
            session.status = "Aborted" if self._is_cancelled else "Completed"

            self.scan_finished.emit(session)

        except Exception as e:
            logger.error(f"Discovery scan exception: {e}", exc_info=True)
            self.scan_failed.emit(str(e))


class PortScanWorker(QThread):
    progress_changed = Signal(int, int, int)
    port_discovered = Signal(object)
    scan_finished = Signal(object)
    scan_failed = Signal(str)

    def __init__(self, target_ip: str, port_list: List[int], timeout: float = 0.4, threads: int = 150):
        super().__init__()
        self.target_ip = target_ip
        self.port_list = port_list
        self.timeout = timeout
        self.threads = threads
        self.engine = PortScannerEngine(timeout=timeout, max_threads=threads)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        self.engine.cancel()

    def run(self):
        t0 = time.time()
        start_dt = datetime.now()
        session = ScanSession(
            scan_type="Port Scan",
            target_range=f"{self.target_ip} ({len(self.port_list)} ports)",
            start_time=start_dt
        )

        try:
            def on_progress(current, total, port):
                self.progress_changed.emit(current, total, port)

            def on_port(p: PortInfo):
                self.port_discovered.emit(p)

            open_ports = self.engine.scan_ports(
                self.target_ip,
                self.port_list,
                progress_callback=on_progress,
                port_found_callback=on_port
            )

            banners = [p.banner for p in open_ports if p.banner]
            os_guess = OSDetector.refine_os_from_banners(banners, "Unknown")

            device = DeviceInfo(
                ip=self.target_ip,
                hostname=self._get_hostname(self.target_ip),
                os_detected=os_guess,
                response_time_ms=(time.time() - t0) * 1000,
                status="Active",
                open_ports=open_ports
            )

            session.devices = [device]
            session.total_hosts_found = 1 if open_ports else 0
            session.total_ports_scanned = len(self.port_list)
            session.total_open_ports = len(open_ports)
            session.end_time = datetime.now()
            session.duration_seconds = time.time() - t0
            session.status = "Aborted" if self._is_cancelled else "Completed"

            self.scan_finished.emit(session)

        except Exception as e:
            logger.error(f"Port scan exception: {e}", exc_info=True)
            self.scan_failed.emit(str(e))

    def _get_hostname(self, ip: str) -> str:
        import socket
        try:
            h, _, _ = socket.gethostbyaddr(ip)
            return h
        except Exception:
            return "Unknown"
