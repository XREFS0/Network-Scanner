"""Professional dark theme stylesheet, clean typography, and polished UI design tokens."""

class Theme:
    # Sleek dark developer palette (similar to Datadog, Snyk, Wireshark, GitHub dark dim)
    BG_MAIN = "#0f1318"
    BG_SIDEBAR = "#090d11"
    BG_PANEL = "#151b23"
    BG_CARD = "#19212b"
    BG_INPUT = "#0d1117"
    BG_HOVER = "#212b38"
    BG_ACTIVE = "#1c2a3e"

    # Borders
    BORDER_DARK = "#212833"
    BORDER_LIGHT = "#303946"
    BORDER_FOCUS = "#388bfd"

    # Accents (Subtle, balanced, professional)
    ACCENT_BLUE = "#2f81f7"
    ACCENT_CYAN = "#38bdf8"
    ACCENT_GREEN = "#2ea043"
    ACCENT_AMBER = "#d29922"
    ACCENT_RED = "#f85149"
    ACCENT_PURPLE = "#a371f7"

    # Typography colors
    TEXT_PRIMARY = "#f0f6fc"
    TEXT_SECONDARY = "#9198a1"
    TEXT_MUTED = "#656c76"

    FONT_SANS = "Segoe UI, -apple-system, BlinkMacSystemFont, 'SF Pro Text', Roboto, sans-serif"
    FONT_MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, 'Fira Code', monospace"


GLOBAL_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0f1318;
    color: #f0f6fc;
    font-family: Segoe UI, -apple-system, BlinkMacSystemFont, 'SF Pro Text', Roboto, sans-serif;
    font-size: 13px;
}

#CentralWidget {
    background-color: #0f1318;
}

/* Sidebar */
#SidebarWidget {
    background-color: #090d11;
    border-right: 1px solid #212833;
}

#BrandContainer {
    background-color: transparent;
    padding: 10px 12px 14px 12px;
    border-bottom: 1px solid #212833;
}

#BrandTitle {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: #58a6ff;
}

#BrandSub {
    font-size: 11px;
    color: #656c76;
}

#SectionLabel {
    font-size: 10px;
    font-weight: 700;
    color: #656c76;
    letter-spacing: 0.8px;
    padding-left: 6px;
}

/* Navigation buttons */
QPushButton.nav-btn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #9198a1;
    text-align: left;
    padding: 9px 12px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.nav-btn:hover {
    background-color: #212b38;
    color: #f0f6fc;
}

QPushButton.nav-btn:checked {
    background-color: #1c2a3e;
    color: #58a6ff;
    border: 1px solid #1f3b61;
    font-weight: 600;
}

/* Panels and Cards */
QFrame.panel-box {
    background-color: #151b23;
    border: 1px solid #212833;
    border-radius: 6px;
}

QFrame.metric-card {
    background-color: #19212b;
    border: 1px solid #212833;
    border-radius: 6px;
}

QFrame.metric-card:hover {
    border-color: #303946;
}

/* Clean Data Tables */
QTableWidget, QTableView {
    background-color: #0d1117;
    border: 1px solid #212833;
    border-radius: 4px;
    gridline-color: #1c232d;
    color: #f0f6fc;
    selection-background-color: #1c324e;
    selection-color: #ffffff;
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, 'Fira Code', monospace;
    font-size: 12px;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #161d26;
}

QHeaderView::section {
    background-color: #151b23;
    color: #9198a1;
    padding: 7px 10px;
    border: none;
    border-bottom: 1px solid #212833;
    border-right: 1px solid #212833;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* Buttons */
QPushButton.btn-primary {
    background-color: #2f81f7;
    color: #ffffff;
    border: 1px solid #408bf7;
    border-radius: 5px;
    font-weight: 600;
    padding: 7px 16px;
    font-size: 12px;
}

QPushButton.btn-primary:hover {
    background-color: #1f6feb;
}

QPushButton.btn-primary:pressed {
    background-color: #1a5ac2;
}

QPushButton.btn-primary:disabled {
    background-color: #21262d;
    border-color: #303946;
    color: #656c76;
}

QPushButton.btn-secondary {
    background-color: #151b23;
    color: #f0f6fc;
    border: 1px solid #303946;
    border-radius: 5px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.btn-secondary:hover {
    background-color: #212b38;
    border-color: #485466;
}

QPushButton.btn-danger {
    background-color: #3a1d22;
    color: #ff7b72;
    border: 1px solid #852a32;
    border-radius: 5px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton.btn-danger:hover {
    background-color: #6e272d;
    color: #ffffff;
}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #0d1117;
    border: 1px solid #303946;
    border-radius: 5px;
    color: #f0f6fc;
    padding: 6px 10px;
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, 'Fira Code', monospace;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #388bfd;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #151b23;
    border: 1px solid #212833;
    color: #f0f6fc;
    selection-background-color: #212b38;
    selection-color: #38bdf8;
}

/* Progress Bar */
QProgressBar {
    background-color: #0d1117;
    border: 1px solid #212833;
    border-radius: 4px;
    text-align: center;
    color: #f0f6fc;
    font-size: 11px;
    font-weight: 600;
    height: 14px;
}

QProgressBar::chunk {
    background-color: #2f81f7;
    border-radius: 3px;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #0f1318;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #212833;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #303946;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Splitters */
QSplitter::handle {
    background-color: #212833;
    height: 2px;
}

/* Log View */
QPlainTextEdit.log-box {
    background-color: #0d1117;
    border: 1px solid #212833;
    border-radius: 5px;
    color: #c9d1d9;
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, 'Fira Code', monospace;
    font-size: 12px;
}
"""
