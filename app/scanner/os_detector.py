from typing import Optional


class OSDetector:
    @staticmethod
    def detect_os_from_ttl(ttl: Optional[int]) -> str:
        if ttl is None or ttl <= 0:
            return "Unknown"

        if ttl <= 64:
            return "Linux / Unix / Android / macOS"
        elif ttl <= 128:
            return "Windows 10/11/Server"
        elif ttl <= 255:
            return "Cisco IOS / BSD / Solaris"
        return "Unknown"

    @staticmethod
    def refine_os_from_banners(banners: list[str], ttl_guess: str = "Unknown") -> str:
        combined = " ".join([b.lower() for b in banners if b])

        if "microsoft-iis" in combined or "windows" in combined or "win32" in combined:
            return "Windows Server / Desktop"
        if "ubuntu" in combined:
            return "Ubuntu Linux"
        if "debian" in combined:
            return "Debian Linux"
        if "centos" in combined or "red hat" in combined or "rhel" in combined:
            return "Red Hat / CentOS Enterprise Linux"
        if "apache" in combined and "unix" in combined:
            return "Linux / Unix Server"
        if "dropbear" in combined or "openwrt" in combined:
            return "Embedded Linux / OpenWrt Router"
        if "microhttpd" in combined or "espressif" in combined:
            return "Embedded IoT / ESP32"

        return ttl_guess
