from dataclasses import dataclass, field
from typing import List, Optional
from app.models.port import PortInfo


@dataclass
class DeviceInfo:
    ip: str
    mac: str = "Unknown"
    hostname: str = "Unknown"
    vendor: str = "Unknown"
    os_detected: str = "Unknown"
    response_time_ms: float = 0.0
    status: str = "Active"
    ttl: Optional[int] = None
    open_ports: List[PortInfo] = field(default_factory=list)

    @property
    def open_port_count(self) -> int:
        return len([p for p in self.open_ports if p.state.lower() == "open"])

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "mac": self.mac,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "os_detected": self.os_detected,
            "response_time_ms": round(self.response_time_ms, 2),
            "status": self.status,
            "ttl": self.ttl,
            "open_port_count": self.open_port_count,
            "open_ports": [p.to_dict() for p in self.open_ports]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceInfo":
        ports = [PortInfo.from_dict(p) for p in data.get("open_ports", [])]
        return cls(
            ip=data.get("ip", ""),
            mac=data.get("mac", "Unknown"),
            hostname=data.get("hostname", "Unknown"),
            vendor=data.get("vendor", "Unknown"),
            os_detected=data.get("os_detected", "Unknown"),
            response_time_ms=float(data.get("response_time_ms", 0.0)),
            status=data.get("status", "Active"),
            ttl=data.get("ttl"),
            open_ports=ports
        )
