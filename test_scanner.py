"""Automated test suite verifying core components, models, database, and validation logic."""
import unittest
import os
import tempfile
import sqlite3
from datetime import datetime

from app.models.device import DeviceInfo
from app.models.port import PortInfo
from app.models.session import ScanSession
from app.utils.validator import TargetValidator
from app.utils.exporter import ReportExporter
from app.scanner.oui_lookup import lookup_vendor
from app.scanner.os_detector import OSDetector
from app.scanner.network_detector import NetworkDetector
from app.database.db_manager import DatabaseManager
from app.database.repository import ScanRepository


class TestNetworkScanner(unittest.TestCase):
    def test_target_validator_single_ip(self):
        targets = TargetValidator.validate_and_expand_target("192.168.1.50")
        self.assertEqual(targets, ["192.168.1.50"])

    def test_target_validator_cidr(self):
        targets = TargetValidator.validate_and_expand_target("192.168.1.0/30")
        self.assertEqual(len(targets), 2)  # .1 and .2
        self.assertIn("192.168.1.1", targets)
        self.assertIn("192.168.1.2", targets)

    def test_target_validator_range(self):
        targets = TargetValidator.validate_and_expand_target("10.0.0.1-5")
        self.assertEqual(len(targets), 5)
        self.assertEqual(targets[0], "10.0.0.1")
        self.assertEqual(targets[-1], "10.0.0.5")

    def test_port_validator(self):
        ports = TargetValidator.parse_port_range("80, 443, 8000-8003")
        self.assertEqual(ports, [80, 443, 8000, 8001, 8002, 8003])

    def test_oui_vendor_lookup(self):
        vendor = lookup_vendor("00:03:93:12:34:56")
        self.assertEqual(vendor, "Apple")
        vendor_intel = lookup_vendor("00-02-B3-AA-BB-CC")
        self.assertEqual(vendor_intel, "Intel")

    def test_os_detector(self):
        self.assertIn("Linux", OSDetector.detect_os_from_ttl(64))
        self.assertIn("Windows", OSDetector.detect_os_from_ttl(128))
        self.assertIn("Cisco", OSDetector.detect_os_from_ttl(255))
        refined = OSDetector.refine_os_from_banners(["Server: Microsoft-IIS/10.0"])
        self.assertIn("Windows", refined)

    def test_database_and_repository(self):
        repo = ScanRepository()
        session = ScanSession(
            scan_type="Quick Scan",
            target_range="192.168.1.0/24",
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=1.5,
            total_hosts_found=1,
            total_ports_scanned=20,
            total_open_ports=1,
            status="Completed"
        )
        dev = DeviceInfo(
            ip="192.168.1.100",
            mac="00:11:22:33:44:55",
            hostname="desktop-node.local",
            vendor="TestVendor",
            os_detected="Windows 11",
            response_time_ms=2.5,
            status="Active"
        )
        port = PortInfo(port=80, protocol="TCP", state="Open", service="HTTP", banner="Apache/2.4")
        dev.open_ports.append(port)
        session.devices.append(dev)

        session_id = repo.save_session(session)
        self.assertIsNotNone(session_id)

        loaded = repo.get_session_by_id(session_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.target_range, "192.168.1.0/24")
        self.assertEqual(len(loaded.devices), 1)
        self.assertEqual(loaded.devices[0].ip, "192.168.1.100")
        self.assertEqual(len(loaded.devices[0].open_ports), 1)
        self.assertEqual(loaded.devices[0].open_ports[0].port, 80)

    def test_reporters(self):
        session = ScanSession(
            scan_type="Full Scan",
            target_range="192.168.1.1",
            duration_seconds=0.45,
            total_hosts_found=1,
            total_open_ports=1
        )
        dev = DeviceInfo(ip="192.168.1.1", mac="00:03:93:00:11:22", vendor="Apple")
        dev.open_ports.append(PortInfo(port=443, service="HTTPS"))
        session.devices.append(dev)

        with tempfile.TemporaryDirectory() as tmp_dir:
            json_file = os.path.join(tmp_dir, "test.json")
            csv_file = os.path.join(tmp_dir, "test.csv")
            txt_file = os.path.join(tmp_dir, "test.txt")

            self.assertTrue(ReportExporter.export_to_json(session, json_file))
            self.assertTrue(ReportExporter.export_to_csv(session, csv_file))
            self.assertTrue(ReportExporter.export_to_txt(session, txt_file))

            self.assertTrue(os.path.exists(json_file))
            self.assertTrue(os.path.exists(csv_file))
            self.assertTrue(os.path.exists(txt_file))


if __name__ == "__main__":
    unittest.main()
