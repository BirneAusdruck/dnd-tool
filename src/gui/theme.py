COLORS = {
    "bg": "#1e1e2e",
    "sidebar": "#181825",
    "surface": "#313244",
    "overlay": "#45475a",
    "text": "#cdd6f4",
    "subtext": "#bac2de",
    "muted": "#6c7086",
    "accent": "#c41e3a",
    "gold": "#f5c518",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "error": "#f38ba8",
    "border": "#45475a",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLORS["bg"]};
    color: {COLORS["text"]};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 14px;
}}

QWidget#sidebar {{
    background-color: {COLORS["sidebar"]};
    border-right: 1px solid {COLORS["border"]};
}}

QPushButton#nav-btn {{
    background: transparent;
    color: {COLORS["subtext"]};
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
}}
QPushButton#nav-btn:hover {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
}}
QPushButton#nav-btn:checked {{
    background-color: {COLORS["accent"]};
    color: white;
    font-weight: bold;
}}

QPushButton#primary-btn {{
    background-color: {COLORS["accent"]};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}}
QPushButton#primary-btn:hover {{
    background-color: #e02244;
}}
QPushButton#primary-btn:disabled {{
    background-color: {COLORS["overlay"]};
    color: {COLORS["muted"]};
}}

QPushButton#secondary-btn {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 16px;
}}
QPushButton#secondary-btn:hover {{
    background-color: {COLORS["overlay"]};
}}

QGroupBox {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: bold;
    color: {COLORS["subtext"]};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: {COLORS["subtext"]};
}}

QLineEdit {{
    background-color: {COLORS["bg"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
}}
QLineEdit:focus {{
    border-color: {COLORS["accent"]};
}}

QLabel {{
    color: {COLORS["text"]};
    background: transparent;
}}

QLabel#title {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS["text"]};
}}

QLabel#stat-value {{
    font-size: 28px;
    font-weight: bold;
    color: {COLORS["accent"]};
}}

QLabel#stat-label {{
    font-size: 11px;
    color: {COLORS["muted"]};
    text-transform: uppercase;
}}

QLabel#status-online {{
    color: {COLORS["success"]};
    font-weight: bold;
}}
QLabel#status-offline {{
    color: {COLORS["error"]};
    font-weight: bold;
}}

QStackedWidget {{
    background-color: {COLORS["bg"]};
}}

QMessageBox {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
}}

QDialog {{
    background-color: {COLORS["bg"]};
    color: {COLORS["text"]};
}}

QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    background-color: {COLORS["surface"]};
    border-radius: 6px;
}}
QTabBar::tab {{
    background-color: {COLORS["sidebar"]};
    color: {COLORS["subtext"]};
    padding: 8px 20px;
    border: 1px solid {COLORS["border"]};
}}
QTabBar::tab:selected {{
    background-color: {COLORS["accent"]};
    color: white;
}}
QTabBar::tab:hover:!selected {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text"]};
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QFrame#separator {{
    background-color: {COLORS["border"]};
    max-height: 1px;
}}
"""
