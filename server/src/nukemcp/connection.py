"""Socket client for talking to the NukeMCP addon running inside Nuke.

Opens a fresh connection per request rather than keeping one persistent
socket -- this sidesteps stale-buffer/half-read/reconnect bugs entirely,
at the cost of one extra TCP handshake per call, which on loopback is
sub-millisecond and irrelevant next to the actual Nuke-API work being
dispatched on the other end.
"""

import json
import socket
import uuid

from . import constants


class NukeConnectionError(RuntimeError):
    """Could not reach the Nuke addon, or it returned a malformed response."""


class NukeToolError(RuntimeError):
    """The addon reached Nuke and Nuke's API raised while executing the tool."""

    def __init__(self, message, error_type="NukeApiError"):
        super().__init__(message)
        self.error_type = error_type


def send_request(tool: str, params: dict) -> dict:
    host, port = constants.get_host(), constants.get_port()
    request_id = uuid.uuid4().hex
    payload = (json.dumps({"id": request_id, "tool": tool, "params": params}) + "\n").encode(
        constants.ENCODING
    )

    try:
        with socket.create_connection((host, port), timeout=constants.SOCKET_TIMEOUT_SECONDS) as sock:
            sock.sendall(payload)
            raw_line = _read_one_line(sock)
    except ConnectionRefusedError as exc:
        raise NukeConnectionError(
            "Could not connect to Nuke on {}:{} -- make sure Nuke is running "
            "and the NukeMCP addon is started (Nuke menu: NukeMCP > Start Server).".format(host, port)
        ) from exc
    except socket.timeout as exc:
        raise NukeConnectionError("Timed out waiting for Nuke at {}:{}.".format(host, port)) from exc
    except OSError as exc:
        raise NukeConnectionError("Socket error talking to Nuke at {}:{}: {}".format(host, port, exc)) from exc

    try:
        response = json.loads(raw_line.decode(constants.ENCODING))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise NukeConnectionError(
            "Invalid response from Nuke addon at {}:{}: {}".format(host, port, exc)
        ) from exc

    if response.get("status") == "error":
        raise NukeToolError(
            response.get("message", "unknown error"), response.get("error_type", "NukeApiError")
        )
    return response.get("result")


def _read_one_line(sock) -> bytes:
    buf = bytearray()
    while b"\n" not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf.extend(chunk)
    if not buf:
        raise NukeConnectionError("Empty response from Nuke addon")
    line, _sep, _rest = buf.partition(b"\n")
    return bytes(line)
