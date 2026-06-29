"""Wire-protocol constants for talking to the Nuke-side addon.

KEEP IN SYNC WITH: nuke_addon/nukemcp_server/constants.py
The two files are never imported across processes (this one runs in the
standalone server's venv; the other runs inside Nuke's bundled Python) so
they are kept identical by convention plus tests/test_protocol.py, not by
a shared import.
"""

import os

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9787

HOST_ENV_VAR = "NUKEMCP_HOST"
PORT_ENV_VAR = "NUKEMCP_PORT"

SOCKET_TIMEOUT_SECONDS = 60.0
ENCODING = "utf-8"


def get_host():
    return os.environ.get(HOST_ENV_VAR, DEFAULT_HOST)


def get_port():
    return int(os.environ.get(PORT_ENV_VAR, str(DEFAULT_PORT)))
