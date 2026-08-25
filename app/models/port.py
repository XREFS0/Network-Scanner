from dataclasses import dataclass
from typing import Optional


@dataclass
class PortInfo:
    port: int
    protocol: str = "TCP"
    state: str = "Open"
    service: str = "Unknown"
    banner: Optional[str] = None
    response_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "port": self.port,
            "protocol": self.protocol,
            "state": self.state,
            "service": self.service,
            "banner": self.banner or "",
            "response_time_ms": round(self.response_time_ms, 2)
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PortInfo":
        return cls(
            port=int(data.get("port", 0)),
            protocol=data.get("protocol", "TCP"),
            state=data.get("state", "Open"),
            service=data.get("service", "Unknown"),
            banner=data.get("banner"),
            response_time_ms=float(data.get("response_time_ms", 0.0))
        )
