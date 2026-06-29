"""Socket listener + the thread-safety bridge into Nuke's main thread.

INVARIANT: nothing in this file except the call to `dispatch.handle()` may
touch the `nuke` module's stateful APIs (node graph, knobs, scripts, etc).
Everything else here -- the accept loop, per-connection handling, JSON
framing -- runs on background threads and only ever does socket/JSON work.
`dispatch.handle()` is invoked via `nuke.executeInMainThreadWithResult`,
which is the one safe bridge from a background thread into Nuke's main
thread; Nuke's own docs warn that calling it FROM the main thread will
hang Nuke, so this module must never run on the main thread itself.
"""

import json
import socket
import threading

import nuke

from . import constants, dispatch

_server_socket = None
_accept_thread = None
_stop_event = threading.Event()
_lock = threading.Lock()


def is_running():
    return _server_socket is not None


def start_listener():
    global _server_socket, _accept_thread

    with _lock:
        if _server_socket is not None:
            nuke.tprint("[NukeMCP] already running on {}:{}".format(*_bound_address()))
            return

        host = constants.get_host()
        port = constants.get_port()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError as exc:
            sock.close()
            nuke.tprint(
                "[NukeMCP] failed to bind {}:{} ({}). If this isn't already "
                "running, another process may be using this port -- set the "
                "{} environment variable to use a different one.".format(
                    host, port, exc, constants.PORT_ENV_VAR
                )
            )
            return
        sock.listen(5)

        _server_socket = sock
        _stop_event.clear()
        _accept_thread = threading.Thread(target=_accept_loop, args=(sock,), daemon=True)
        _accept_thread.start()
        nuke.tprint("[NukeMCP] listener started on {}:{}".format(host, port))


def stop_listener():
    global _server_socket, _accept_thread

    with _lock:
        if _server_socket is None:
            nuke.tprint("[NukeMCP] not running")
            return
        _stop_event.set()
        try:
            _server_socket.close()
        except OSError:
            pass
        _server_socket = None
        _accept_thread = None
        nuke.tprint("[NukeMCP] listener stopped")


def show_status():
    if is_running():
        host, port = _bound_address()
        nuke.message("NukeMCP: listening on {}:{}".format(host, port))
    else:
        nuke.message("NukeMCP: not running")


def _bound_address():
    return constants.get_host(), constants.get_port()


def _accept_loop(sock):
    sock.settimeout(1.0)
    while not _stop_event.is_set():
        try:
            conn, _addr = sock.accept()
        except socket.timeout:
            continue
        except OSError:
            break  # socket was closed by stop_listener()
        threading.Thread(target=_handle_connection, args=(conn,), daemon=True).start()


def _handle_connection(conn):
    buf = bytearray()
    try:
        conn.settimeout(constants.SOCKET_TIMEOUT_SECONDS)
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
            while b"\n" in buf:
                line, _sep, rest = buf.partition(b"\n")
                buf = bytearray(rest)
                _process_one_message(conn, bytes(line))
    except (ConnectionResetError, socket.timeout, OSError):
        pass  # client disconnected or went quiet -- not worth logging loudly
    finally:
        try:
            conn.close()
        except OSError:
            pass


def _process_one_message(conn, raw_line):
    request_id = None
    try:
        request = json.loads(raw_line.decode(constants.ENCODING))
        request_id = request.get("id")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        _send_response(conn, {
            "id": request_id, "status": "error",
            "message": "invalid JSON: {}".format(exc), "error_type": "ProtocolError",
        })
        return

    try:
        # THE CRITICAL CALL -- the only safe way for this background thread
        # to touch Nuke's API. Blocks until dispatch.handle() finishes on
        # the main thread, then returns its result.
        #
        # dispatch.handle() never raises -- it always returns an {"ok": ...}
        # envelope -- because exceptions raised inside the dispatched callable
        # do NOT cross back out of executeInMainThreadWithResult (confirmed
        # empirically: Nuke's own wrapper catches them, logs a traceback to
        # Nuke's console, and this call just returns None). The try/except
        # here is defense in depth for executeInMainThreadWithResult itself
        # misbehaving, not the normal error path.
        outcome = nuke.executeInMainThreadWithResult(dispatch.handle, args=(request,))
    except Exception as exc:
        _send_response(conn, {
            "id": request_id, "status": "error",
            "message": str(exc), "error_type": type(exc).__name__,
        })
        return

    if not isinstance(outcome, dict):
        _send_response(conn, {
            "id": request_id, "status": "error",
            "message": "handler produced no result -- check Nuke's console/log for a traceback",
            "error_type": "InternalError",
        })
        return

    if outcome.get("ok"):
        _send_response(conn, {"id": request_id, "status": "ok", "result": outcome.get("result")})
    else:
        _send_response(conn, {
            "id": request_id, "status": "error",
            "message": outcome.get("message"), "error_type": outcome.get("error_type"),
        })


def _send_response(conn, response):
    payload = (json.dumps(response) + "\n").encode(constants.ENCODING)
    try:
        conn.sendall(payload)
    except OSError:
        pass  # client already gone -- nothing to do
