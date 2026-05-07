import sys
import time
import logging

import requests
from PySide6.QtWidgets import QApplication, QMessageBox

from src.client.gui.server_thread import FlaskServerThread
from src.client.gui.main_window import MainWindow
from src.client.gui.theme import STYLESHEET

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)


def _wait_for_server(url: str, timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            requests.get(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DnD Tool")
    app.setOrganizationName("DnDTool")
    app.setStyleSheet(STYLESHEET)

    # Start embedded Flask server in background thread
    server = FlaskServerThread()
    server.start()

    health_url = f"http://127.0.0.1:{server.flask_app.config['SERVER_PORT']}/api/health"
    if not _wait_for_server(health_url):
        QMessageBox.critical(None, "Startfehler", "Der interne Server konnte nicht gestartet werden.")
        sys.exit(1)

    window = MainWindow(server)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
