import socket
import time
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Optional, Dict

from app.models.device import DeviceInfo
from app.scanner.oui_lookup import lookup_vendor
from app.utils.validator import TargetValidator
from app.core.logger import logger

try:
    from scapy.all import ARP, Ether, srp, conf
    conf.verb = 0
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class NetworkDiscoveryEngine:
    def __init__(self, timeout: float = 1.0, max_threads: int = 100):
        self.timeout = timeout
        self.max_threads = max_threads
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def scan(
        self,
        target_range: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        host_found_callback: Optional[Callable[[DeviceInfo], None]] = None
    ) -> List[DeviceInfo]:
        self._is_cancelled = False
        target_ips = TargetValidator.validate_and_expand_target(target_range)
        total_targets = len(target_ips)
        discovered_devices: List[DeviceInfo] = []

        logger.info(f"Starting host discovery for {total_targets} target IP(s)...")

        scapy_success = False
        if SCAPY_AVAILABLE:
            try:
                scapy_results = self._scapy_arp_scan(target_range, target_ips, host_found_callback, progress_callback)
                if scapy_results:
                    discovered_devices.extend(scapy_results)
                    scapy_success = True
            except Exception as e:
                logger.debug(f"Scapy ARP scan bypassed or failed: {e}. Falling back to socket discovery.")

        if not scapy_success and not self._is_cancelled:
            discovered_devices = self._socket_threaded_scan(
                target_ips, progress_callback, host_found_callback
            )

        logger.info(f"Discovery complete. Found {len(discovered_devices)} active host(s).")
        return discovered_devices

    def _scapy_arp_scan(
        self,
        target_range: str,
        target_ips: List[str],
        host_found_callback: Optional[Callable[[DeviceInfo], None]],
        progress_callback: Optional[Callable[[int, int, str], None]]
    ) -> Optional[List[DeviceInfo]]:
        devices: List[DeviceInfo] = []
        arp = ARP(pdst=target_range if "/" in target_range else target_ips)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        ans, _ = srp(packet, timeout=self.timeout, retry=1, verbose=False)
        total = len(target_ips)

        for idx, (sent, received) in enumerate(ans):
            if self._is_cancelled:
                break
            ip = received.psrc
            mac = received.hwsrc.upper()
            hostname = self._resolve_hostname(ip)
            vendor = lookup_vendor(mac)

            t0 = time.time()
            dev = DeviceInfo(
                ip=ip,
                mac=mac,
                hostname=hostname,
                vendor=vendor,
                os_detected="Unknown",
                response_time_ms=(time.time() - t0) * 1000,
                status="Active"
            )
            devices.append(dev)
            if host_found_callback:
                host_found_callback(dev)
            if progress_callback:
                progress_callback(idx + 1, total, ip)

        return devices if devices else None

    def _socket_threaded_scan(
        self,
        target_ips: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]],
        host_found_callback: Optional[Callable[[DeviceInfo], None]]
    ) -> List[DeviceInfo]:
        devices: List[DeviceInfo] = []
        total = len(target_ips)
        processed = 0

        arp_table = self._read_system_arp_table()

        with ThreadPoolExecutor(max_workers=min(self.max_threads, total)) as executor:
            future_to_ip = {executor.submit(self._probe_single_host, ip): ip for ip in target_ips}

            for future in as_completed(future_to_ip):
                if self._is_cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                processed += 1
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    if result:
                        if result.ip in arp_table:
                            result.mac = arp_table[result.ip]
                            result.vendor = lookup_vendor(result.mac)

                        devices.append(result)
                        if host_found_callback:
                            host_found_callback(result)
                except Exception as e:
                    logger.debug(f"Host probe error for {ip}: {e}")

                if progress_callback:
                    progress_callback(processed, total, ip)

        updated_arp = self._read_system_arp_table()
        for dev in devices:
            if dev.mac == "Unknown" and dev.ip in updated_arp:
                dev.mac = updated_arp[dev.ip]
                dev.vendor = lookup_vendor(dev.mac)

        return devices

    def _probe_single_host(self, ip: str) -> Optional[DeviceInfo]:
        probe_ports = [80, 445, 135, 22, 443, 8080, 53, 3389]
        t0 = time.perf_counter()

        for port in probe_ports:
            if self._is_cancelled:
                return None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.timeout / 2.0)
                res = s.connect_ex((ip, port))
                latency_ms = (time.perf_counter() - t0) * 1000
                s.close()

                if res == 0 or res == 10061:
                    hostname = self._resolve_hostname(ip)
                    return DeviceInfo(
                        ip=ip,
                        mac="Unknown",
                        hostname=hostname,
                        vendor="Unknown",
                        os_detected="Unknown",
                        response_time_ms=latency_ms,
                        status="Active"
                    )
            except Exception:
                continue

        if self._ping_host(ip):
            hostname = self._resolve_hostname(ip)
            return DeviceInfo(
                ip=ip,
                mac="Unknown",
                hostname=hostname,
                vendor="Unknown",
                os_detected="Unknown",
                response_time_ms=(time.perf_counter() - t0) * 1000,
                status="Active"
            )

        return None

    def _ping_host(self, ip: str) -> bool:
        try:
            cmd = ["ping", "-n", "1", "-w", str(int(self.timeout * 800)), ip]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0
        except Exception:
            return False

    def _resolve_hostname(self, ip: str) -> str:
        try:
            host, _, _ = socket.gethostbyaddr(ip)
            return host
        except Exception:
            return "Unknown"

    def _read_system_arp_table(self) -> Dict[str, str]:
        table = {}
        try:
            output = subprocess.check_output("arp -a", shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F\-]{17}|[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})\s+(\w+)", line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).replace("-", ":").upper()
                    if mac != "FF:FF:FF:FF:FF:FF":
                        table[ip] = mac
        except Exception as e:
            logger.debug(f"Failed to read system ARP table: {e}")
        return table
