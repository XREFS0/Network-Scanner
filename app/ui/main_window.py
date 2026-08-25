"""Main Application Window integrating sidebar navigation and multi-view stack."""
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

from app.ui.theme import GLOBAL_STYLESHEET
from app.ui.components.sidebar import SidebarWidget
from app.ui.components.log_viewer import LogViewerWidget
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.discovery_view import DiscoveryView
from app.ui.views.port_view import PortScannerView
from app.ui.views.history_view import HistoryView
from app.ui.views.settings_view import SettingsView
from app.database.repository import ScanRepository
from app.core.config import AppConfig
from app.core.logger import logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(AppConfig.APP_NAME)
        self.resize(1200, 780)
        self.setMinimumSize(950, 600)

        # Apply Global Dark Cybersecurity Stylesheet
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # Initialize Data Access Repository
        self.repository = ScanRepository()

        # Root Central Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar navigation
        self.sidebar = SidebarWidget()
        self.sidebar.navigation_changed.connect(self._on_navigation_changed)
        main_layout.addWidget(self.sidebar)

        # View stack
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # Initialize Sub-Views
        self.dashboard_view = DashboardView(self.repository)
        self.discovery_view = DiscoveryView(self.repository)
        self.port_view = PortScannerView(self.repository)
        self.history_view = HistoryView(self.repository)
        self.log_view = LogViewerWidget()
        self.settings_view = SettingsView()

        # Connect inter-view signals
        self.dashboard_view.navigate_to_scan.connect(self._on_dashboard_navigate)
        self.discovery_view.request_port_scan.connect(self._on_request_port_scan)

        # Add to stack in index order matching sidebar buttons:
        # 0: Dashboard, 1: Network Discovery, 2: Port Scanner, 3: Scan History, 4: Live Logs, 5: Settings
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.discovery_view)
        self.stack.addWidget(self.port_view)
        self.stack.addWidget(self.history_view)
        self.stack.addWidget(self.log_view)
        self.stack.addWidget(self.settings_view)

        logger.info(f"{AppConfig.APP_NAME} initialized successfully.")

    def _on_navigation_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard_view.refresh_dashboard()
        elif index == 3:
            self.history_view.load_history()

    def _on_dashboard_navigate(self, target: str):
        if target == "discovery":
            self.sidebar.set_active_page(1)
        elif target == "ports":
            self.sidebar.set_active_page(2)

    def _on_request_port_scan(self, target_ip: str):
        self.port_view.set_target_host(target_ip)
        self.sidebar.set_active_page(2)
