from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from app.models.device import DeviceInfo


@dataclass
class ScanSession:
    id: Optional[int] = None
    scan_type: str = "Quick Scan"
    target_range: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_hosts_found: int = 0
    total_ports_scanned: int = 0
    total_open_ports: int = 0
    status: str = "Completed"
    devices: List[DeviceInfo] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scan_type": self.scan_type,
            "target_range": self.target_range,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.start_time, datetime) else str(self.start_time),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.end_time, datetime) and self.end_time else "",
            "duration_seconds": round(self.duration_seconds, 2),
            "total_hosts_found": self.total_hosts_found,
            "total_ports_scanned": self.total_ports_scanned,
            "total_open_ports": self.total_open_ports,
            "status": self.status,
            "devices": [d.to_dict() for d in self.devices]
        }
