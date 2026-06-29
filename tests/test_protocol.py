"""Confirms the two independently-maintained constants.py files (one runs
inside Nuke's bundled Python, one runs in the standalone server's venv --
they never import each other) haven't drifted apart.
"""

import importlib.util
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SYNCED_NAMES = ("DEFAULT_HOST", "DEFAULT_PORT", "HOST_ENV_VAR", "PORT_ENV_VAR", "ENCODING")


def _load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_constants():
    addon = _load_module_from_path(
        "addon_constants", REPO_ROOT / "nuke_addon" / "nukemcp_server" / "constants.py"
    )
    server = _load_module_from_path(
        "server_constants", REPO_ROOT / "server" / "src" / "nukemcp" / "constants.py"
    )
    return addon, server


def test_constants_are_in_sync():
    addon, server = _load_constants()
    for name in SYNCED_NAMES:
        assert getattr(addon, name) == getattr(server, name), (
            "constants.py drift on {}: addon={!r} server={!r}".format(
                name, getattr(addon, name), getattr(server, name)
            )
        )


def test_ndjson_round_trip():
    import json

    request = {"id": "abc", "tool": "get_script_info", "params": {}}
    line = (json.dumps(request) + "\n").encode("utf-8")
    assert line.endswith(b"\n")
    assert json.loads(line.decode("utf-8").rstrip("\n")) == request
