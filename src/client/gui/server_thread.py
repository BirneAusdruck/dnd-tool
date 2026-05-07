import threading
import logging
from flask import Flask
from src.server.app import create_app
from src.server.extensions import socketio
from config import Config

log = logging.getLogger(__name__)


class FlaskServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="flask-server")
        self.flask_app: Flask = create_app()

    def run(self) -> None:
        log.info("Starting Flask server on %s:%d", Config.SERVER_HOST, Config.SERVER_PORT)
        socketio.run(
            self.flask_app,
            host=Config.SERVER_HOST,
            port=Config.SERVER_PORT,
            use_reloader=False,
            log_output=False,
            allow_unsafe_werkzeug=True,
        )
