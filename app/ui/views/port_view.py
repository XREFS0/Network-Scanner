from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.models.port import PortInfo
from app.models.session import ScanSession
from app.scanner.worker import PortScanWorker
from app.database.repository import ScanRepository
from app.utils.validator import TargetValidator
from app.utils.exporter import ReportExporter
from app.core.config import AppConfig
from app.ui.theme import Theme
from app.core.logger import logger


class PortScannerView(QWidget):
    def __init__(self, repository: ScanRepository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self.worker: PortScanWorker = None
        self.current_session: ScanSession = None
        self.discovered_ports: list[PortInfo] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Port Scanner")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc;")
        sub_title = QLabel("Probe open TCP services, identify service banners, and assess exposed endpoints")
        sub_title.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY};")
        title_box.addWidget(title)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        controls_frame = QFrame()
        controls_frame.setProperty("class", "panel-box")
        c_layout = QHBoxLayout(controls_frame)
        c_layout.setContentsMargins(14, 12, 14, 12)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("Target IP:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.1 or example.com")
        self.host_input.setMinimumWidth(180)
        c_layout.addWidget(self.host_input)

        c_layout.addWidget(QLabel("Port Profile:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(AppConfig.PORT_PRESETS.keys()) + ["Custom Range..."])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        c_layout.addWidget(self.preset_combo)

        self.ports_input = QLineEdit()
        self.ports_input.setPlaceholderText("e.g. 80,443,8000-8080")
        self.ports_input.setText(", ".join(map(str, AppConfig.PORT_PRESETS["Quick (Top 20)"])))
        self.ports_input.setMinimumWidth(200)
        c_layout.addWidget(self.ports_input)

        self.btn_scan = QPushButton("Start Port Scan")
        self.btn_scan.setProperty("class", "btn-primary")
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.clicked.connect(self.toggle_scan)
        c_layout.addWidget(self.btn_scan)

        self.btn_export = QPushButton("Export")
        self.btn_export.setProperty("class", "btn-secondary")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self._show_export_menu)
        c_layout.addWidget(self.btn_export)

        layout.addWidget(controls_frame)

        p_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY}; font-family: {Theme.FONT_MONO};")

        p_layout.addWidget(self.status_label)
        p_layout.addWidget(self.progress_bar, 1)
        layout.addLayout(p_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter open ports by port number, service, or banner...")
        self.search_input.textChanged.connect(self._filter_table)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Port", "Protocol", "State", "Service Name", "Response Latency", "Banner / Details"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def set_target_host(self, host_ip: str):
        self.host_input.setText(host_ip)

    def _on_preset_changed(self, preset_name: str):
        if preset_name in AppConfig.PORT_PRESETS:
            ports = AppConfig.PORT_PRESETS[preset_name]
            self.ports_input.setText(", ".join(map(str, ports)))
        else:
            self.ports_input.clear()
            self.ports_input.setFocus()

    def toggle_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Cancelling port scan...")
            self.btn_scan.setEnabled(False)
            return

        target_ip = self.host_input.text().strip()
        ports_str = self.ports_input.text().strip()

        if not target_ip:
            QMessageBox.warning(self, "Validation Error", "Please provide a valid target host or IP.")
            return

        try:
            port_list = TargetValidator.parse_port_range(ports_str)
        except Exception as e:
            QMessageBox.warning(self, "Port Syntax Error", str(e))
            return

        self.discovered_ports.clear()
        self.table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_scan.setText("Stop Scan")
        self.btn_scan.setProperty("class", "btn-danger")
        self.btn_scan.style().unpolish(self.btn_scan)
        self.btn_scan.style().polish(self.btn_scan)
        self.status_label.setText(f"Scanning {len(port_list)} ports on {target_ip}...")

        self.worker = PortScanWorker(
            target_ip=target_ip,
            port_list=port_list,
            timeout=0.4,
            threads=150
        )
        self.worker.progress_changed.connect(self._on_progress)
        self.worker.port_discovered.connect(self._on_port_found)
        self.worker.scan_finished.connect(self._on_scan_finished)
        self.worker.scan_failed.connect(self._on_scan_failed)
        self.worker.start()

    def _on_progress(self, current: int, total: int, port: int):
        pct = int((current / max(1, total)) * 100)
        self.progress_bar.setValue(pct)
        self.status_label.setText(f"Scanning [{current}/{total}] - Testing TCP port {port}...")

    def _on_port_found(self, port_info: PortInfo):
        self.discovered_ports.append(port_info)
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(port_info.port)))
        self.table.setItem(row, 1, QTableWidgetItem(port_info.protocol))

        state_item = QTableWidgetItem(port_info.state)
        state_item.setForeground(QColor(Theme.ACCENT_GREEN))
        self.table.setItem(row, 2, state_item)

        self.table.setItem(row, 3, QTableWidgetItem(port_info.service))
        self.table.setItem(row, 4, QTableWidgetItem(f"{port_info.response_time_ms:.1f} ms"))
        self.table.setItem(row, 5, QTableWidgetItem(port_info.banner or ""))

    def _on_scan_finished(self, session: ScanSession):
        self.current_session = session
        self.progress_bar.setVisible(False)
        self._reset_scan_button()
        self.status_label.setText(
            f"Port scan complete. Found {session.total_open_ports} open port(s) in {session.duration_seconds:.2f}s."
        )
        try:
            self.repo.save_session(session)
        except Exception as e:
            logger.error(f"Failed to auto-save port session: {e}")

    def _on_scan_failed(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self._reset_scan_button()
        self.status_label.setText("Scan failed.")
        QMessageBox.critical(self, "Port Scan Error", f"Scan failed:\n{error_msg}")

    def _reset_scan_button(self):
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Start Port Scan")
        self.btn_scan.setProperty("class", "btn-primary")
        self.btn_scan.style().unpolish(self.btn_scan)
        self.btn_scan.style().polish(self.btn_scan)

    def _filter_table(self, query: str):
        q = query.lower().strip()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and q in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def _show_export_menu(self):
        if not self.current_session:
            QMessageBox.information(self, "Export", "No completed port scan results to export.")
            return

        menu = QMenu(self)
        json_act = menu.addAction("Export to JSON (.json)")
        csv_act = menu.addAction("Export to CSV (.csv)")
        txt_act = menu.addAction("Export to Security Report (.txt)")

        action = menu.exec(self.btn_export.mapToGlobal(self.btn_export.rect().bottomLeft()))
        if not action:
            return

        if action == json_act:
            self._export_file("JSON (*.json)", ReportExporter.export_to_json, ".json")
        elif action == csv_act:
            self._export_file("CSV (*.csv)", ReportExporter.export_to_csv, ".csv")
        elif action == txt_act:
            self._export_file("Text Report (*.txt)", ReportExporter.export_to_txt, ".txt")

    def _export_file(self, filter_str: str, export_fn, default_ext: str):
        path, _ = QFileDialog.getSaveFileName(self, "Save Export File", f"port_scan_report{default_ext}", filter_str)
        if path:
            try:
                export_fn(self.current_session, path)
                QMessageBox.information(self, "Export Complete", f"Report successfully saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
