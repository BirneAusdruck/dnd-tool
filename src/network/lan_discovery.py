"""
LAN Discovery – UDP broadcast beacon.

The server repeatedly broadcasts a JSON packet on the local network so that
mobile clients can find it without manual IP entry.

Broadcast port:  54321
Interval:        2 s
Payload:         {type, name, ip, port, url, version}
"""
from __future__ import annotations
import json
import socket
import threading
import time

BROADCAST_PORT = 54321
INTERVAL = 2.0
_VERSION = "0.1.0"


def get_local_ip() -> str:
    """Best-effort: returns the LAN IP of the current machine."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


class LanDiscovery:
    """Periodically broadcasts server presence on the LAN."""

    def __init__(self, server_port: int, server_name: str = "DnD Tool GM"):
        self._port = server_port
        self._name = server_name
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="lan-discovery"
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

    # ── Internal ──────────────────────────────────────────────────────────

    def _loop(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        try:
            while self._running:
                try:
                    ip = get_local_ip()
                    payload = json.dumps({
                        "type":    "dndtool_server",
                        "name":    self._name,
                        "ip":      ip,
                        "port":    self._port,
                        "url":     f"http://{ip}:{self._port}",
                        "version": _VERSION,
                    }).encode()
                    sock.sendto(payload, ("255.255.255.255", BROADCAST_PORT))
                except Exception:
                    pass
                time.sleep(INTERVAL)
        finally:
            sock.close()


class LanScanner:
    """
    Listens for LAN broadcasts from DnD Tool servers.
    Used by mobile / player clients to auto-discover a GM server.
    Results are collected in `servers` dict keyed by IP.
    """

    def __init__(self):
        self.servers: dict[str, dict] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._listen, daemon=True, name="lan-scanner"
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _listen(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1.0)
        try:
            sock.bind(("", BROADCAST_PORT))
            while self._running:
                try:
                    data, addr = sock.recvfrom(1024)
                    info = json.loads(data.decode())
                    if info.get("type") == "dndtool_server":
                        self.servers[addr[0]] = info
                except (socket.timeout, json.JSONDecodeError):
                    pass
        finally:
            sock.close()
