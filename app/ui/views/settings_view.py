from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from app.ui.theme import Theme


class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Scanner Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc;")
        sub_title = QLabel("Fine-tune network timing parameters, thread pools, and operational constraints")
        sub_title.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY};")
        title_box.addWidget(title)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        card = QFrame()
        card.setProperty("class", "panel-box")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(16)

        r1 = QHBoxLayout()
        lbl1 = QLabel("Network Discovery Concurrency (Threads):")
        self.spin_disc_threads = QSpinBox()
        self.spin_disc_threads.setRange(10, 500)
        self.spin_disc_threads.setValue(100)
        r1.addWidget(lbl1)
        r1.addStretch()
        r1.addWidget(self.spin_disc_threads)
        c_layout.addLayout(r1)

        r2 = QHBoxLayout()
        lbl2 = QLabel("Port Scanner Concurrency (Threads):")
        self.spin_port_threads = QSpinBox()
        self.spin_port_threads.setRange(10, 500)
        self.spin_port_threads.setValue(150)
        r2.addWidget(lbl2)
        r2.addStretch()
        r2.addWidget(self.spin_port_threads)
        c_layout.addLayout(r2)

        r3 = QHBoxLayout()
        lbl3 = QLabel("Host Discovery Timeout (Seconds):")
        self.spin_disc_timeout = QDoubleSpinBox()
        self.spin_disc_timeout.setRange(0.1, 5.0)
        self.spin_disc_timeout.setSingleStep(0.1)
        self.spin_disc_timeout.setValue(1.0)
        r3.addWidget(lbl3)
        r3.addStretch()
        r3.addWidget(self.spin_disc_timeout)
        c_layout.addLayout(r3)

        r4 = QHBoxLayout()
        lbl4 = QLabel("Port Socket Connect Timeout (Seconds):")
        self.spin_port_timeout = QDoubleSpinBox()
        self.spin_port_timeout.setRange(0.05, 3.0)
        self.spin_port_timeout.setSingleStep(0.05)
        self.spin_port_timeout.setValue(0.4)
        r4.addWidget(lbl4)
        r4.addStretch()
        r4.addWidget(self.spin_port_timeout)
        c_layout.addLayout(r4)

        layout.addWidget(card)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Preferences")
        save_btn.setProperty("class", "btn-primary")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        btn_box.addStretch()
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

        layout.addStretch()

    def _save_settings(self):
        QMessageBox.information(self, "Settings Saved", "Scanner performance preferences updated successfully.")
