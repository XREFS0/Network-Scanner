from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "network_scanner.db"
LOG_FILE_PATH = LOGS_DIR / "scanner.log"


class AppConfig:
    APP_NAME: str = "NetSentinel"
    APP_VERSION: str = "2.4.0"
    ORGANIZATION: str = "XREFS0"
    DEFAULT_TIMEOUT: float = 0.5
    DEFAULT_THREADS: int = 100
    MAX_THREADS: int = 500
    DEFAULT_ARP_TIMEOUT: float = 1.2
    DEFAULT_PORT_TIMEOUT: float = 0.4

    PORT_PRESETS: Dict[str, List[int]] = {
        "Quick (Top 20)": [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
            143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080
        ],
        "Standard (Top 100)": [
            20, 21, 22, 23, 25, 53, 67, 68, 69, 80,
            88, 110, 111, 119, 123, 135, 137, 138, 139, 143,
            161, 162, 179, 389, 443, 445, 465, 514, 515, 587,
            636, 993, 995, 1080, 1433, 1434, 1521, 1723, 2049, 2082,
            2083, 2086, 2087, 2181, 2222, 3000, 3128, 3306, 3389, 4000,
            4444, 5000, 5432, 5672, 5900, 5985, 5986, 6379, 6667, 7000,
            7001, 8000, 8008, 8080, 8081, 8443, 8888, 9000, 9090, 9200,
            9300, 9418, 9999, 11211, 27017, 27018, 28017, 50000, 50070
        ],
        "Web & Cloud": [
            80, 443, 8080, 8443, 8000, 8008, 8888, 3000, 5000, 9000, 9090
        ],
        "Remote Management": [
            22, 23, 3389, 5900, 5901, 5985, 5986, 2222
        ],
        "Databases": [
            1433, 1521, 3306, 5432, 6379, 27017, 9200, 9300, 11211
        ]
    }


COMMON_SERVICES: Dict[int, str] = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "HTTP",
    88: "Kerberos",
    110: "POP3",
    111: "RPCBind",
    119: "NNTP",
    123: "NTP",
    135: "MS-RPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    179: "BGP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    587: "Submission",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1433: "MSSQL",
    1434: "MSSQL-Monitor",
    1521: "Oracle",
    1723: "PPTP",
    2049: "NFS",
    2082: "cPanel",
    2083: "cPanel-SSL",
    2181: "ZooKeeper",
    2222: "SSH-Alt",
    3000: "Node/React-Dev",
    3128: "Squid-Proxy",
    3306: "MySQL",
    3389: "RDP",
    4444: "Metasploit",
    5000: "Flask/Docker",
    5432: "PostgreSQL",
    5672: "RabbitMQ",
    5900: "VNC",
    5985: "WinRM-HTTP",
    5986: "WinRM-HTTPS",
    6379: "Redis",
    6667: "IRC",
    7000: "Cassandra",
    8000: "HTTP-Alt",
    8080: "HTTP-Proxy",
    8081: "Blackice-Icecap",
    8443: "HTTPS-Alt",
    8888: "HTTP-Alt",
    9000: "SonarQube/Portainer",
    9090: "Prometheus",
    9200: "Elasticsearch",
    9300: "Elasticsearch-Cluster",
    11211: "Memcached",
    27017: "MongoDB",
    27018: "MongoDB-Shard",
}
