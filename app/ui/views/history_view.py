from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QMenu, QSplitter
)
from PySide6.QtCore import Qt
from app.database.repository import ScanRepository
from app.utils.exporter import ReportExporter
from app.ui.theme import Theme
from app.core.logger import logger


class HistoryView(QWidget):
    def __init__(self, repository: ScanRepository, parent=None):
        super().__init__(parent)
        self.repo = repository

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Scan History")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc;")
        sub_title = QLabel("Browse historical scan sessions, inspect discovered targets, and export previous audits")
        sub_title.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY};")
        title_box.addWidget(title)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        bar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.setProperty("class", "btn-secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_history)

        self.btn_export_sel = QPushButton("Export Selected Session")
        self.btn_export_sel.setProperty("class", "btn-secondary")
        self.btn_export_sel.setCursor(Qt.PointingHandCursor)
        self.btn_export_sel.clicked.connect(self._export_selected)

        self.btn_delete_sel = QPushButton("Delete Session")
        self.btn_delete_sel.setProperty("class", "btn-danger")
        self.btn_delete_sel.setCursor(Qt.PointingHandCursor)
        self.btn_delete_sel.clicked.connect(self._delete_selected)

        bar.addWidget(refresh_btn)
        bar.addStretch()
        bar.addWidget(self.btn_export_sel)
        bar.addWidget(self.btn_delete_sel)
        layout.addLayout(bar)

        splitter = QSplitter(Qt.Vertical)

        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(7)
        self.sessions_table.setHorizontalHeaderLabels([
            "ID", "Scan Type", "Target Range", "Timestamp", "Duration", "Hosts Found", "Status"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sessions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sessions_table.verticalHeader().setVisible(False)
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sessions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sessions_table.itemSelectionChanged.connect(self._on_session_selected)
        splitter.addWidget(self.sessions_table)

        self.details_table = QTableWidget()
        self.details_table.setColumnCount(6)
        self.details_table.setHorizontalHeaderLabels([
            "Host IP", "MAC Address", "Hostname", "Vendor", "OS Fingerprint", "Open Ports"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.details_table.verticalHeader().setVisible(False)
        self.details_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.details_table.setEditTriggers(QTableWidget.NoEditTriggers)
        splitter.addWidget(self.details_table)

        layout.addWidget(splitter)
        self.load_history()

    def load_history(self):
        try:
            sessions = self.repo.get_all_sessions(limit=100)
            self.sessions_table.setRowCount(len(sessions))
            for row, s in enumerate(sessions):
                self.sessions_table.setItem(row, 0, QTableWidgetItem(str(s.id)))
                self.sessions_table.setItem(row, 1, QTableWidgetItem(s.scan_type))
                self.sessions_table.setItem(row, 2, QTableWidgetItem(s.target_range))
                self.sessions_table.setItem(row, 3, QTableWidgetItem(s.start_time.strftime("%Y-%m-%d %H:%M:%S")))
                self.sessions_table.setItem(row, 4, QTableWidgetItem(f"{s.duration_seconds:.2f}s"))
                self.sessions_table.setItem(row, 5, QTableWidgetItem(str(s.total_hosts_found)))
                self.sessions_table.setItem(row, 6, QTableWidgetItem(s.status))
            self.details_table.setRowCount(0)
        except Exception as e:
            logger.error(f"Failed to load scan history: {e}")

    def _on_session_selected(self):
        selected = self.sessions_table.currentRow()
        if selected < 0:
            return
        id_item = self.sessions_table.item(selected, 0)
        if not id_item:
            return
        session_id = int(id_item.text())

        session = self.repo.get_session_by_id(session_id)
        if not session:
            return

        self.details_table.setRowCount(len(session.devices))
        for row, d in enumerate(session.devices):
            ports_summary = ", ".join([str(p.port) for p in d.open_ports if p.state == "Open"]) or "None"
            self.details_table.setItem(row, 0, QTableWidgetItem(d.ip))
            self.details_table.setItem(row, 1, QTableWidgetItem(d.mac))
            self.details_table.setItem(row, 2, QTableWidgetItem(d.hostname))
            self.details_table.setItem(row, 3, QTableWidgetItem(d.vendor))
            self.details_table.setItem(row, 4, QTableWidgetItem(d.os_detected))
            self.details_table.setItem(row, 5, QTableWidgetItem(ports_summary))

    def _export_selected(self):
        selected = self.sessions_table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Export", "Please select a session row first.")
            return
        session_id = int(self.sessions_table.item(selected, 0).text())
        session = self.repo.get_session_by_id(session_id)
        if not session:
            return

        menu = QMenu(self)
        json_act = menu.addAction("Export to JSON (.json)")
        csv_act = menu.addAction("Export to CSV (.csv)")
        txt_act = menu.addAction("Export to Security Report (.txt)")

        action = menu.exec(self.btn_export_sel.mapToGlobal(self.btn_export_sel.rect().bottomLeft()))
        if not action:
            return

        if action == json_act:
            self._export_file(session, "JSON (*.json)", ReportExporter.export_to_json, ".json")
        elif action == csv_act:
            self._export_file(session, "CSV (*.csv)", ReportExporter.export_to_csv, ".csv")
        elif action == txt_act:
            self._export_file(session, "Text Report (*.txt)", ReportExporter.export_to_txt, ".txt")

    def _export_file(self, session, filter_str: str, export_fn, default_ext: str):
        path, _ = QFileDialog.getSaveFileName(self, "Save Export File", f"scan_session_{session.id}{default_ext}", filter_str)
        if path:
            try:
                export_fn(session, path)
                QMessageBox.information(self, "Export Complete", f"Report successfully saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _delete_selected(self):
        selected = self.sessions_table.currentRow()
        if selected < 0:
            return
        session_id = int(self.sessions_table.item(selected, 0).text())
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete scan session #{session_id} from SQLite database?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.repo.delete_session(session_id)
            self.load_history()
