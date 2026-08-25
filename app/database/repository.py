from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database.db_manager import DatabaseManager
from app.models.session import ScanSession
from app.models.device import DeviceInfo
from app.models.port import PortInfo
from app.core.logger import logger


class ScanRepository:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def save_session(self, session: ScanSession) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            start_str = session.start_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(session.start_time, datetime) else str(session.start_time)
            end_str = session.end_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(session.end_time, datetime) and session.end_time else None

            cursor.execute(
                """
                INSERT INTO scan_sessions (
                    scan_type, target_range, start_time, end_time,
                    duration_seconds, total_hosts_found, total_ports_scanned,
                    total_open_ports, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.scan_type,
                    session.target_range,
                    start_str,
                    end_str,
                    session.duration_seconds,
                    session.total_hosts_found,
                    session.total_ports_scanned,
                    session.total_open_ports,
                    session.status
                )
            )
            session_id = cursor.lastrowid
            session.id = session_id

            for dev in session.devices:
                cursor.execute(
                    """
                    INSERT INTO devices (
                        session_id, ip, mac, hostname, vendor,
                        os_detected, response_time_ms, status, ttl
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        dev.ip,
                        dev.mac,
                        dev.hostname,
                        dev.vendor,
                        dev.os_detected,
                        dev.response_time_ms,
                        dev.status,
                        dev.ttl
                    )
                )
                device_id = cursor.lastrowid

                for p in dev.open_ports:
                    cursor.execute(
                        """
                        INSERT INTO ports (
                            device_id, port, protocol, state,
                            service, banner, response_time_ms
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            device_id,
                            p.port,
                            p.protocol,
                            p.state,
                            p.service,
                            p.banner,
                            p.response_time_ms
                        )
                    )

            logger.info(f"Scan session #{session_id} successfully persisted to SQLite.")
            return session_id

    def get_all_sessions(self, limit: int = 50) -> List[ScanSession]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, scan_type, target_range, start_time, end_time,
                       duration_seconds, total_hosts_found, total_ports_scanned,
                       total_open_ports, status
                FROM scan_sessions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            sessions = []
            for r in rows:
                try:
                    st = datetime.strptime(r["start_time"], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    st = datetime.now()
                et = None
                if r["end_time"]:
                    try:
                        et = datetime.strptime(r["end_time"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass

                sess = ScanSession(
                    id=r["id"],
                    scan_type=r["scan_type"],
                    target_range=r["target_range"],
                    start_time=st,
                    end_time=et,
                    duration_seconds=r["duration_seconds"],
                    total_hosts_found=r["total_hosts_found"],
                    total_ports_scanned=r["total_ports_scanned"],
                    total_open_ports=r["total_open_ports"],
                    status=r["status"]
                )
                sessions.append(sess)
            return sessions

    def get_session_by_id(self, session_id: int) -> Optional[ScanSession]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_sessions WHERE id = ?", (session_id,))
            s_row = cursor.fetchone()
            if not s_row:
                return None

            try:
                st = datetime.strptime(s_row["start_time"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                st = datetime.now()
            et = None
            if s_row["end_time"]:
                try:
                    et = datetime.strptime(s_row["end_time"], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass

            session = ScanSession(
                id=s_row["id"],
                scan_type=s_row["scan_type"],
                target_range=s_row["target_range"],
                start_time=st,
                end_time=et,
                duration_seconds=s_row["duration_seconds"],
                total_hosts_found=s_row["total_hosts_found"],
                total_ports_scanned=s_row["total_ports_scanned"],
                total_open_ports=s_row["total_open_ports"],
                status=s_row["status"]
            )

            cursor.execute("SELECT * FROM devices WHERE session_id = ?", (session_id,))
            d_rows = cursor.fetchall()
            for d in d_rows:
                dev = DeviceInfo(
                    ip=d["ip"],
                    mac=d["mac"] or "Unknown",
                    hostname=d["hostname"] or "Unknown",
                    vendor=d["vendor"] or "Unknown",
                    os_detected=d["os_detected"] or "Unknown",
                    response_time_ms=d["response_time_ms"] or 0.0,
                    status=d["status"] or "Active",
                    ttl=d["ttl"]
                )
                cursor.execute("SELECT * FROM ports WHERE device_id = ?", (d["id"],))
                p_rows = cursor.fetchall()
                for p in p_rows:
                    port_info = PortInfo(
                        port=p["port"],
                        protocol=p["protocol"] or "TCP",
                        state=p["state"] or "Open",
                        service=p["service"] or "Unknown",
                        banner=p["banner"],
                        response_time_ms=p["response_time_ms"] or 0.0
                    )
                    dev.open_ports.append(port_info)
                session.devices.append(dev)

            return session

    def delete_session(self, session_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_scans FROM scan_sessions")
            total_scans = cursor.fetchone()["total_scans"]

            cursor.execute("SELECT COUNT(*) as total_devices FROM devices")
            total_devices = cursor.fetchone()["total_devices"]

            cursor.execute("SELECT COUNT(*) as total_open_ports FROM ports WHERE state = 'Open'")
            total_open_ports = cursor.fetchone()["total_open_ports"]

            return {
                "total_scans": total_scans,
                "total_devices": total_devices,
                "total_open_ports": total_open_ports
            }
