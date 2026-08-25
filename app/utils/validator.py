import ipaddress
from typing import List
from app.core.exceptions import InvalidTargetError


class TargetValidator:
    @staticmethod
    def validate_and_expand_target(target_str: str) -> List[str]:
        target = target_str.strip()
        if not target:
            raise InvalidTargetError("Target address cannot be empty.")

        if "/" in target:
            try:
                network = ipaddress.ip_network(target, strict=False)
                if network.num_addresses > 65536:
                    raise InvalidTargetError("Network range too large (max /16 allowed).")
                return [str(ip) for ip in network.hosts()]
            except ValueError as e:
                raise InvalidTargetError(f"Invalid CIDR notation '{target}': {e}")

        if "-" in target:
            parts = target.split("-")
            if len(parts) == 2:
                start_part, end_part = parts[0].strip(), parts[1].strip()
                try:
                    start_ip = ipaddress.IPv4Address(start_part)
                    if "." in end_part:
                        end_ip = ipaddress.IPv4Address(end_part)
                    else:
                        octets = start_part.split(".")
                        end_ip = ipaddress.IPv4Address(f"{octets[0]}.{octets[1]}.{octets[2]}.{end_part}")

                    if int(start_ip) > int(end_ip):
                        raise InvalidTargetError(f"Start IP {start_ip} is greater than End IP {end_ip}.")

                    count = int(end_ip) - int(start_ip) + 1
                    if count > 65536:
                        raise InvalidTargetError("IP range too large (max 65,536 hosts).")

                    return [str(ipaddress.IPv4Address(ip_int)) for ip_int in range(int(start_ip), int(end_ip) + 1)]
                except ValueError as e:
                    raise InvalidTargetError(f"Invalid IP range '{target}': {e}")

        if "," in target:
            hosts = []
            for item in target.split(","):
                item_str = item.strip()
                if item_str:
                    hosts.extend(TargetValidator.validate_and_expand_target(item_str))
            return list(dict.fromkeys(hosts))

        try:
            ip = ipaddress.IPv4Address(target)
            return [str(ip)]
        except ValueError:
            import socket
            try:
                resolved_ip = socket.gethostbyname(target)
                return [resolved_ip]
            except socket.gaierror:
                raise InvalidTargetError(f"Unable to resolve host or IP address '{target}'.")

    @staticmethod
    def parse_port_range(port_str: str) -> List[int]:
        if not port_str or not port_str.strip():
            raise InvalidTargetError("Port range cannot be empty.")

        ports = set()
        chunks = [c.strip() for c in port_str.split(",") if c.strip()]

        for chunk in chunks:
            if "-" in chunk:
                parts = chunk.split("-")
                if len(parts) != 2:
                    raise InvalidTargetError(f"Invalid port range chunk '{chunk}'.")
                try:
                    start_p = int(parts[0].strip())
                    end_p = int(parts[1].strip())
                    if not (1 <= start_p <= 65535 and 1 <= end_p <= 65535):
                        raise InvalidTargetError("Port numbers must be between 1 and 65535.")
                    if start_p > end_p:
                        raise InvalidTargetError(f"Start port {start_p} > end port {end_p}.")
                    ports.update(range(start_p, end_p + 1))
                except ValueError:
                    raise InvalidTargetError(f"Invalid port numbers in '{chunk}'.")
            else:
                try:
                    p = int(chunk)
                    if not (1 <= p <= 65535):
                        raise InvalidTargetError(f"Port {p} is out of valid range (1-65535).")
                    ports.add(p)
                except ValueError:
                    raise InvalidTargetError(f"Invalid port value '{chunk}'.")

        return sorted(list(ports))
