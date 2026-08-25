-- SQLite Database Schema for NetSentinel Scanner

CREATE TABLE IF NOT EXISTS scan_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type TEXT NOT NULL,
    target_range TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_seconds REAL DEFAULT 0.0,
    total_hosts_found INTEGER DEFAULT 0,
    total_ports_scanned INTEGER DEFAULT 0,
    total_open_ports INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Completed'
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    ip TEXT NOT NULL,
    mac TEXT,
    hostname TEXT,
    vendor TEXT,
    os_detected TEXT,
    response_time_ms REAL DEFAULT 0.0,
    status TEXT DEFAULT 'Active',
    ttl INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    port INTEGER NOT NULL,
    protocol TEXT DEFAULT 'TCP',
    state TEXT DEFAULT 'Open',
    service TEXT DEFAULT 'Unknown',
    banner TEXT,
    response_time_ms REAL DEFAULT 0.0,
    FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scan_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    log_level TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_devices_session ON devices(session_id);
CREATE INDEX IF NOT EXISTS idx_ports_device ON ports(device_id);
CREATE INDEX IF NOT EXISTS idx_logs_session ON scan_logs(session_id);
