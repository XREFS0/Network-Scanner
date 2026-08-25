import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Optional

from app.models.port import PortInfo
from app.core.config import COMMON_SERVICES
from app.core.logger import logger


class PortScannerEngine:
    def __init__(self, timeout: float = 0.5, max_threads: int = 150):
        self.timeout = timeout
        self.max_threads = max_threads
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def scan_ports(
        self,
        host_ip: str,
        ports: List[int],
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
        port_found_callback: Optional[Callable[[PortInfo], None]] = None
    ) -> List[PortInfo]:
        self._is_cancelled = False
        total = len(ports)
        open_ports: List[PortInfo] = []
        processed = 0

        logger.info(f"Initiating TCP port scan on {host_ip} for {total} port(s)...")

        with ThreadPoolExecutor(max_workers=min(self.max_threads, total)) as executor:
            future_to_port = {executor.submit(self._scan_single_port, host_ip, p): p for p in ports}

            for future in as_completed(future_to_port):
                if self._is_cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                processed += 1
                port = future_to_port[future]
                try:
                    res = future.result()
                    if res and res.state == "Open":
                        open_ports.append(res)
                        if port_found_callback:
                            port_found_callback(res)
                except Exception as e:
                    logger.debug(f"Error scanning port {port}: {e}")

                if progress_callback:
                    progress_callback(processed, total, port)

        open_ports.sort(key=lambda x: x.port)
        logger.info(f"Port scan completed on {host_ip}. Found {len(open_ports)} open port(s).")
        return open_ports

    def _scan_single_port(self, host_ip: str, port: int) -> Optional[PortInfo]:
        t0 = time.perf_counter()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)

        try:
            res = s.connect_ex((host_ip, port))
            latency_ms = (time.perf_counter() - t0) * 1000

            if res == 0:
                service_name = COMMON_SERVICES.get(port, "Unknown")
                banner = self._grab_banner(s, host_ip, port)

                if service_name == "Unknown" and banner:
                    service_name = self._infer_service_from_banner(banner)

                return PortInfo(
                    port=port,
                    protocol="TCP",
                    state="Open",
                    service=service_name,
                    banner=banner,
                    response_time_ms=latency_ms
                )
            return None
        except Exception:
            return None
        finally:
            try:
                s.close()
            except Exception:
                pass

    def _grab_banner(self, s: socket.socket, host_ip: str, port: int) -> Optional[str]:
        try:
            s.settimeout(0.3)
            banner_bytes = s.recv(512)
            if banner_bytes:
                return banner_bytes.decode("utf-8", errors="ignore").strip()

            if port in (80, 443, 8080, 8443, 8000, 3000, 5000):
                probe = f"HEAD / HTTP/1.0\r\nHost: {host_ip}\r\nUser-Agent: NetSentinel\r\n\r\n".encode()
                s.sendall(probe)
                resp = s.recv(512).decode("utf-8", errors="ignore").strip()
                if resp:
                    first_line = resp.split("\n")[0].strip()
                    for line in resp.splitlines():
                        if line.lower().startswith("server:"):
                            return f"{first_line} | {line.strip()}"
                    return first_line

            return None
        except Exception:
            return None

    def _infer_service_from_banner(self, banner: str) -> str:
        b_low = banner.lower()
        if "ssh" in b_low:
            return "SSH"
        if "ftp" in b_low:
            return "FTP"
        if "smtp" in b_low or "esmtp" in b_low:
            return "SMTP"
        if "http" in b_low:
            return "HTTP"
        if "mysql" in b_low or "mariadb" in b_low:
            return "MySQL"
        if "redis" in b_low:
            return "Redis"
        return "Unknown"
