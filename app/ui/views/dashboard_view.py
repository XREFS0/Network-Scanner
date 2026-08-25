"""Dashboard view with polished layout, telemetry metrics, and interface discovery."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from app.ui.components.metric_card import MetricCard
from app.scanner.network_detector import NetworkDetector
from app.database.repository import ScanRepository
from app.ui.theme import Theme


class DashboardView(QWidget):
    navigate_to_scan = Signal(str)

    def __init__(self, repository: ScanRepository, parent=None):
        super().__init__(parent)
        self.repo = repository

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title Banner
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        main_title = QLabel("Security Dashboard")
        main_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc;")
        sub_title = QLabel("Network infrastructure telemetry and host reconnaissance overview")
        sub_title.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY};")
        title_box.addWidget(main_title)
        title_box.addWidget(sub_title)

        refresh_btn = QPushButton("Refresh Telemetry")
        refresh_btn.setProperty("class", "btn-secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_dashboard)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Metric Cards Row
        self.metrics_layout = QHBoxLayout()
        self.metrics_layout.setSpacing(12)

        self.card_devices = MetricCard("Discovered Hosts", "0", "Total hosts in database", Theme.ACCENT_CYAN)
        self.card_ports = MetricCard("Open TCP Ports", "0", "Identified network services", Theme.ACCENT_GREEN)
        self.card_scans = MetricCard("Scan Sessions", "0", "Archived history records", Theme.ACCENT_PURPLE)
        self.card_gateway = MetricCard("Default Gateway", "--", "Active network router", Theme.ACCENT_AMBER)

        self.metrics_layout.addWidget(self.card_devices)
        self.metrics_layout.addWidget(self.card_ports)
        self.metrics_layout.addWidget(self.card_scans)
        self.metrics_layout.addWidget(self.card_gateway)
        layout.addLayout(self.metrics_layout)

        # Content Split: Left (Interfaces Table), Right (Quick Operations)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Left: Active Network Interfaces
        left_panel = QFrame()
        left_panel.setProperty("class", "panel-box")
        lp_layout = QVBoxLayout(left_panel)
        lp_layout.setContentsMargins(14, 14, 14, 14)
        lp_layout.setSpacing(10)

        lp_title = QLabel("LOCAL NETWORK ADAPTERS")
        lp_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        lp_layout.addWidget(lp_title)

        self.iface_table = QTableWidget()
        self.iface_table.setColumnCount(4)
        self.iface_table.setHorizontalHeaderLabels(["Interface Name", "IPv4 Address", "Subnet Mask", "Subnet Range"])
        self.iface_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.iface_table.verticalHeader().setVisible(False)
        self.iface_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.iface_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lp_layout.addWidget(self.iface_table)
        content_layout.addWidget(left_panel, 3)

        # Right: Quick Launch Operations & Outbound Host Info
        right_panel = QFrame()
        right_panel.setProperty("class", "panel-box")
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.setContentsMargins(14, 14, 14, 14)
        rp_layout.setSpacing(10)

        rp_title = QLabel("QUICK ACTIONS")
        rp_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        rp_layout.addWidget(rp_title)

        self.btn_quick_discovery = QPushButton("Launch Subnet Discovery")
        self.btn_quick_discovery.setProperty("class", "btn-primary")
        self.btn_quick_discovery.setCursor(Qt.PointingHandCursor)
        self.btn_quick_discovery.clicked.connect(lambda: self.navigate_to_scan.emit("discovery"))

        self.btn_quick_port = QPushButton("Launch Port Scanner")
        self.btn_quick_port.setProperty("class", "btn-secondary")
        self.btn_quick_port.setCursor(Qt.PointingHandCursor)
        self.btn_quick_port.clicked.connect(lambda: self.navigate_to_scan.emit("ports"))

        rp_layout.addWidget(self.btn_quick_discovery)
        rp_layout.addWidget(self.btn_quick_port)
        rp_layout.addStretch()

        # Host telemetry snippet
        telemetry_box = QFrame()
        telemetry_box.setStyleSheet(f"background-color: {Theme.BG_INPUT}; border: 1px solid {Theme.BORDER_DARK}; border-radius: 4px; padding: 8px;")
        tb_layout = QVBoxLayout(telemetry_box)
        tb_layout.setContentsMargins(6, 6, 6, 6)
        tb_layout.setSpacing(4)

        self.lbl_local_ip = QLabel("Outbound IP: Detecting...")
        self.lbl_local_ip.setStyleSheet(f"font-family: {Theme.FONT_MONO}; font-size: 11px; color: {Theme.TEXT_SECONDARY};")
        
        self.lbl_arch = QLabel("Engine: Multi-threaded Socket/ARP")
        self.lbl_arch.setStyleSheet(f"font-family: {Theme.FONT_MONO}; font-size: 10px; color: {Theme.TEXT_MUTED};")

        tb_layout.addWidget(self.lbl_local_ip)
        tb_layout.addWidget(self.lbl_arch)
        rp_layout.addWidget(telemetry_box)

        content_layout.addWidget(right_panel, 2)
        layout.addLayout(content_layout)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        try:
            m = self.repo.get_dashboard_metrics()
            self.card_devices.set_value(str(m["total_devices"]))
            self.card_ports.set_value(str(m["total_open_ports"]))
            self.card_scans.set_value(str(m["total_scans"]))
        except Exception:
            pass

        try:
            local_ip = NetworkDetector.get_local_ip()
            gateway = NetworkDetector.get_default_gateway()
            self.card_gateway.set_value(gateway)
            self.lbl_local_ip.setText(f"Outbound IP: {local_ip}")

            interfaces = NetworkDetector.get_interfaces()
            self.iface_table.setRowCount(len(interfaces))
            for row, iface in enumerate(interfaces):
                self.iface_table.setItem(row, 0, QTableWidgetItem(iface["name"]))
                self.iface_table.setItem(row, 1, QTableWidgetItem(iface["ip"]))
                self.iface_table.setItem(row, 2, QTableWidgetItem(iface["netmask"]))
                self.iface_table.setItem(row, 3, QTableWidgetItem(iface["subnet_range"]))
        except Exception:
            pass
