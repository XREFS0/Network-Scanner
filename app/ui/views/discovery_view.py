from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor

from app.models.device import DeviceInfo
from app.models.session import ScanSession
from app.scanner.network_detector import NetworkDetector
from app.scanner.worker import DiscoveryScanWorker
from app.database.repository import ScanRepository
from app.utils.exporter import ReportExporter
from app.ui.theme import Theme
from app.core.logger import logger


class DiscoveryView(QWidget):
    request_port_scan = Signal(str)

    def __init__(self, repository: ScanRepository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self.worker: DiscoveryScanWorker = None
        self.current_session: ScanSession = None
        self.discovered_devices: list[DeviceInfo] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Network Discovery")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc;")
        sub_title = QLabel("Scan local subnets, detect active hosts, resolve MAC vendors and hardware identifiers")
        sub_title.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY};")
        title_box.addWidget(title)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        controls_frame = QFrame()
        controls_frame.setProperty("class", "panel-box")
        c_layout = QHBoxLayout(controls_frame)
        c_layout.setContentsMargins(14, 12, 14, 12)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("Target / CIDR:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g. 192.168.1.0/24 or 192.168.1.1-50")
        self.target_input.setText(NetworkDetector.get_suggested_subnet())
        self.target_input.setMinimumWidth(220)
        c_layout.addWidget(self.target_input)

        c_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Quick Scan", "Full Scan (with Top Ports)"])
        c_layout.addWidget(self.mode_combo)

        self.btn_scan = QPushButton("Start Discovery")
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

        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search results by IP, MAC, Hostname, Vendor, or OS...")
        self.search_input.textChanged.connect(self._filter_table)
        filter_layout.addWidget(self.search_input)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "IP Address", "MAC Address", "Hostname", "Vendor", "OS Fingerprint", "Latency", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

    def toggle_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Cancelling scan...")
            self.btn_scan.setEnabled(False)
            return

        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Validation Error", "Please specify a target network or IP range.")
            return

        mode = self.mode_combo.currentText()
        self.discovered_devices.clear()
        self.table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_scan.setText("Stop Scan")
        self.btn_scan.setProperty("class", "btn-danger")
        self.btn_scan.style().unpolish(self.btn_scan)
        self.btn_scan.style().polish(self.btn_scan)
        self.status_label.setText(f"Scanning target {target}...")

        self.worker = DiscoveryScanWorker(
            target_range=target,
            scan_type=mode,
            timeout=1.0,
            threads=100
        )
        self.worker.progress_changed.connect(self._on_progress)
        self.worker.host_discovered.connect(self._on_host_found)
        self.worker.scan_finished.connect(self._on_scan_finished)
        self.worker.scan_failed.connect(self._on_scan_failed)
        self.worker.start()

    def _on_progress(self, current: int, total: int, target_ip: str):
        pct = int((current / max(1, total)) * 100)
        self.progress_bar.setValue(pct)
        self.status_label.setText(f"Probing [{current}/{total}]: {target_ip}")

    def _on_host_found(self, dev: DeviceInfo):
        self.discovered_devices.append(dev)
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(dev.ip))
        self.table.setItem(row, 1, QTableWidgetItem(dev.mac))
        self.table.setItem(row, 2, QTableWidgetItem(dev.hostname))
        self.table.setItem(row, 3, QTableWidgetItem(dev.vendor))
        self.table.setItem(row, 4, QTableWidgetItem(dev.os_detected))
        self.table.setItem(row, 5, QTableWidgetItem(f"{dev.response_time_ms:.1f} ms"))

        status_item = QTableWidgetItem(dev.status)
        status_item.setForeground(QColor(Theme.ACCENT_GREEN))
        self.table.setItem(row, 6, status_item)

    def _on_scan_finished(self, session: ScanSession):
        self.current_session = session
        self.progress_bar.setVisible(False)
        self._reset_scan_button()
        self.status_label.setText(
            f"Finished. Found {session.total_hosts_found} active host(s) in {session.duration_seconds:.2f}s."
        )
        try:
            self.repo.save_session(session)
        except Exception as e:
            logger.error(f"Failed to auto-save scan session: {e}")

    def _on_scan_failed(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self._reset_scan_button()
        self.status_label.setText("Scan failed.")
        QMessageBox.critical(self, "Scan Error", f"Discovery scan failed:\n{error_msg}")

    def _reset_scan_button(self):
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Start Discovery")
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

    def _show_context_menu(self, pos):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        ip_item = self.table.item(selected_row, 0)
        if not ip_item:
            return
        target_ip = ip_item.text()

        menu = QMenu(self)
        scan_ports_act = QAction(f"Scan Ports on {target_ip}", self)
        scan_ports_act.triggered.connect(lambda: self.request_port_scan.emit(target_ip))
        menu.addAction(scan_ports_act)

        copy_ip_act = QAction("Copy IP Address", self)
        copy_ip_act.triggered.connect(lambda: self._copy_to_clipboard(target_ip))
        menu.addAction(copy_ip_act)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _show_export_menu(self):
        if not self.current_session or not self.current_session.devices:
            QMessageBox.information(self, "Export", "No completed scan results to export.")
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
        path, _ = QFileDialog.getSaveFileName(self, "Save Export File", f"scan_report{default_ext}", filter_str)
        if path:
            try:
                export_fn(self.current_session, path)
                QMessageBox.information(self, "Export Complete", f"Report successfully saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
