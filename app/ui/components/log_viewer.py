from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QComboBox, QLabel
from app.core.logger import LogEmitter
from app.ui.theme import Theme


class LogViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        bar = QHBoxLayout()
        title = QLabel("Application Logs")
        title.setStyleSheet("font-size: 14px; font-weight: 700;")

        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.level_combo.currentTextChanged.connect(self._apply_filter)

        clear_btn = QPushButton("Clear")
        clear_btn.setProperty("class", "btn-secondary")
        clear_btn.clicked.connect(self.clear_logs)

        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(QLabel("Filter:"))
        bar.addWidget(self.level_combo)
        bar.addWidget(clear_btn)
        layout.addLayout(bar)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setProperty("class", "log-box")
        layout.addWidget(self.text_edit)

        self.log_entries = []
        LogEmitter.register_callback(self._on_log_received)

    def _on_log_received(self, level: str, timestamp: str, message: str):
        entry = (level, timestamp, message)
        self.log_entries.append(entry)
        if len(self.log_entries) > 2000:
            self.log_entries.pop(0)

        selected = self.level_combo.currentText()
        if selected == "ALL" or selected == level:
            self._append_line(level, timestamp, message)

    def _append_line(self, level: str, timestamp: str, message: str):
        color = "#c9d1d9"
        if level == "ERROR":
            color = Theme.ACCENT_RED
        elif level == "WARNING":
            color = Theme.ACCENT_AMBER
        elif level == "DEBUG":
            color = Theme.TEXT_MUTED
        elif level == "INFO":
            color = Theme.ACCENT_CYAN

        formatted = f'<span style="color: {Theme.TEXT_MUTED};">[{timestamp}]</span> <span style="color: {color}; font-weight: 600;">[{level}]</span> <span>{message}</span>'
        self.text_edit.appendHtml(formatted)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def _apply_filter(self):
        self.text_edit.clear()
        selected = self.level_combo.currentText()
        for level, timestamp, message in self.log_entries:
            if selected == "ALL" or selected == level:
                self._append_line(level, timestamp, message)

    def clear_logs(self):
        self.log_entries.clear()
        self.text_edit.clear()
