"""Clean, structured sidebar navigation widget with crisp brand alignment."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QFrame
from PySide6.QtCore import Signal, Qt
from app.ui.theme import Theme
from app.core.config import AppConfig


class SidebarWidget(QWidget):
    navigation_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarWidget")
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            #SidebarWidget {{
                background-color: {Theme.BG_SIDEBAR};
                border-right: 1px solid {Theme.BORDER_DARK};
            }}
            #BrandTitle {{
                font-size: 15px;
                font-weight: 700;
                color: #58a6ff;
                letter-spacing: 1px;
            }}
            #BrandSub {{
                font-size: 11px;
                color: {Theme.TEXT_MUTED};
            }}
            #SectionLabel {{
                font-size: 10px;
                font-weight: 700;
                color: {Theme.TEXT_MUTED};
                letter-spacing: 0.8px;
                padding-left: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Brand header container
        brand_frame = QFrame()
        brand_frame.setObjectName("BrandContainer")
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(4, 4, 4, 8)
        brand_layout.setSpacing(4)

        # Title
        brand_title = QLabel("NETSENTINEL")
        brand_title.setObjectName("BrandTitle")

        brand_sub = QLabel("Network Security & Recon")
        brand_sub.setObjectName("BrandSub")

        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_sub)
        layout.addWidget(brand_frame)
        layout.addSpacing(10)

        # Navigation section title
        section_lbl = QLabel("EXPLORER")
        section_lbl.setObjectName("SectionLabel")
        layout.addWidget(section_lbl)
        layout.addSpacing(2)

        self.buttons = []
        nav_items = [
            ("Dashboard", 0),
            ("Network Discovery", 1),
            ("Port Scanner", 2),
            ("Scan History", 3),
            ("Live Logs", 4),
            ("Settings", 5)
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self._on_btn_clicked(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Footer Status Card
        footer_card = QFrame()
        footer_card.setStyleSheet(f"background-color: {Theme.BG_PANEL}; border: 1px solid {Theme.BORDER_DARK}; border-radius: 5px; padding: 6px;")
        footer_layout = QHBoxLayout(footer_card)
        footer_layout.setContentsMargins(6, 4, 6, 4)
        footer_layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {Theme.ACCENT_GREEN}; font-size: 12px;")
        status_text = QLabel("Scanner Idle")
        status_text.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")

        footer_layout.addWidget(dot)
        footer_layout.addWidget(status_text)
        footer_layout.addStretch()

        layout.addWidget(footer_card)

        # Select Dashboard by default
        if self.buttons:
            self.buttons[0].setChecked(True)

    def _on_btn_clicked(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.navigation_changed.emit(index)

    def set_active_page(self, index: int):
        if 0 <= index < len(self.buttons):
            self._on_btn_clicked(index)
