import threading
import time

active_connections = []


class WebSocketHandler:
    def __init__(self):
        self.connections = []
        self._lock = threading.Lock()

    def on_connect(self, ws):
        self.connections.append({
            "ws": ws,
            "connected_at": time.time(),
            "buffer": bytearray(1024 * 1024),
        })
        active_connections.append(ws)

    def on_message(self, ws, message):
        for conn in self.connections:
            try:
                conn["ws"].send(message)
            except Exception:
                pass

    def on_close(self, ws):
        self.connections = [c for c in self.connections if c["ws"] != ws]

    def get_connection_count(self):
        return len(self.connections)
