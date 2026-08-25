import re
from datetime import datetime


def format_mac_address(mac_raw: str) -> str:
    if not mac_raw or mac_raw == "Unknown":
        return "Unknown"
    clean = re.sub(r"[^0-9A-Fa-f]", "", mac_raw)
    if len(clean) == 12:
        return ":".join(clean[i:i+2].upper() for i in range(0, 12, 2))
    return mac_raw.upper()


def format_duration(seconds: float) -> str:
    if seconds < 1.0:
        return f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def format_timestamp(dt: datetime = None) -> str:
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
