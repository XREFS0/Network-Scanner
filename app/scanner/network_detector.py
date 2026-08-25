import socket
import psutil
import subprocess
import re
from typing import Dict, List
from app.core.logger import logger


class NetworkDetector:
    @staticmethod
    def get_local_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    @staticmethod
    def get_default_gateway() -> str:
        try:
            output = subprocess.check_output("route print 0.0.0.0", shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                    gateway = parts[2]
                    if gateway != "On-link" and re.match(r"^\d+\.\d+\.\d+\.\d+$", gateway):
                        return gateway
        except Exception as e:
            logger.debug(f"Failed to get gateway from route print: {e}")

        local_ip = NetworkDetector.get_local_ip()
        if local_ip and local_ip != "127.0.0.1":
            octets = local_ip.split(".")
            return f"{octets[0]}.{octets[1]}.{octets[2]}.1"
        return "Unknown"

    @staticmethod
    def get_interfaces() -> List[Dict[str, str]]:
        interfaces = []
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        for iface_name, addrs in net_if_addrs.items():
            stats = net_if_stats.get(iface_name)
            is_up = stats.isup if stats else False

            ipv4_addr = None
            netmask = None
            mac_addr = None

            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ipv4_addr = addr.address
                    netmask = addr.netmask
                elif getattr(addr, 'family', None) == psutil.AF_LINK or addr.family == -1 or "AF_LINK" in str(addr.family):
                    mac_addr = addr.address

            if ipv4_addr and not ipv4_addr.startswith("127.") and is_up:
                cidr = 24
                if netmask:
                    try:
                        import ipaddress
                        net = ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False)
                        cidr = net.prefixlen
                    except Exception:
                        cidr = 24

                subnet = f"{ipv4_addr}/{cidr}"
                try:
                    import ipaddress
                    net_obj = ipaddress.IPv4Network(subnet, strict=False)
                    calculated_range = f"{net_obj.network_address}/{cidr}"
                except Exception:
                    calculated_range = subnet

                interfaces.append({
                    "name": iface_name,
                    "ip": ipv4_addr,
                    "netmask": netmask or "255.255.255.0",
                    "mac": mac_addr or "Unknown",
                    "cidr": cidr,
                    "subnet_range": calculated_range,
                    "is_up": is_up
                })

        return interfaces

    @staticmethod
    def get_suggested_subnet() -> str:
        interfaces = NetworkDetector.get_interfaces()
        local_ip = NetworkDetector.get_local_ip()

        for iface in interfaces:
            if iface["ip"] == local_ip:
                return iface["subnet_range"]

        if interfaces:
            return interfaces[0]["subnet_range"]

        if local_ip != "127.0.0.1":
            octets = local_ip.split(".")
            return f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"

        return "192.168.1.0/24"
