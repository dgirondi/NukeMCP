"""A stdlib-only stand-in for the Nuke addon's listener, for tests that
need something speaking the real NDJSON wire protocol without requiring
an actual running Nuke session.

Unlike the real listener (nuke_addon/nukemcp_server/listener.py), this
has no main-thread bridge -- handlers run directly on the connection
thread, since there's no GUI thread to protect here.
"""

import json
import socket
import threading


class FakeNukeListener:
    def __init__(self, handlers=None):
        self.handlers = handlers or {}
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))  # OS-assigned free port
        self._sock.listen(5)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)

    @property
    def port(self):
        return self._sock.getsockname()[1]

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        try:
            self._sock.close()
        except OSError:
            pass
        self._thread.join(timeout=2.0)

    def _accept_loop(self):
        self._sock.settimeout(1.0)
        while not self._stop_event.is_set():
            try:
                conn, _addr = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle_connection, args=(conn,), daemon=True).start()

    def _handle_connection(self, conn):
        buf = bytearray()
        try:
            conn.settimeout(5.0)
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf.extend(chunk)
                while b"\n" in buf:
                    line, _sep, rest = buf.partition(b"\n")
                    buf = bytearray(rest)
                    self._process_one_message(conn, bytes(line))
        except (ConnectionResetError, socket.timeout, OSError):
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def _process_one_message(self, conn, raw_line):
        request = json.loads(raw_line.decode("utf-8"))
        request_id = request.get("id")
        handler = self.handlers.get(request.get("tool"))
        if handler is None:
            response = {
                "id": request_id, "status": "error",
                "message": "no such tool: {!r}".format(request.get("tool")),
                "error_type": "UnknownToolError",
            }
        else:
            try:
                result = handler(request.get("params") or {})
                response = {"id": request_id, "status": "ok", "result": result}
            except Exception as exc:
                response = {
                    "id": request_id, "status": "error",
                    "message": str(exc), "error_type": type(exc).__name__,
                }
        conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
