from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.ui.theme import Theme


class MetricCard(QFrame):
    def __init__(self, title: str, initial_value: str = "0", subtitle: str = "", accent_color: str = Theme.ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setProperty("class", "metric-card")
        self.accent_color = accent_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {Theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")

        self.value_lbl = QLabel(initial_value)
        self.value_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {accent_color}; font-family: {Theme.FONT_MONO};")

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_MUTED};")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.sub_lbl)

    def set_value(self, value: str):
        self.value_lbl.setText(value)

    def set_subtitle(self, text: str):
        self.sub_lbl.setText(text)
