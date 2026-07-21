from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request

# Patterns that are blocked outright before the code reaches Nuke.
# Tuple of (substring_to_match, human_readable_category).
_BLOCKED_PATTERNS: list[tuple[str, str]] = [
    # Destructive filesystem operations
    ("shutil.rmtree",   "filesystem deletion (shutil.rmtree)"),
    ("os.remove(",      "file deletion (os.remove)"),
    ("os.unlink(",      "file deletion (os.unlink)"),
    ("os.rmdir(",       "directory deletion (os.rmdir)"),
    # Process termination — would kill the Nuke session
    ("sys.exit",        "process termination (sys.exit)"),
    ("os._exit",        "process termination (os._exit)"),
    # Arbitrary shell execution
    ("subprocess.Popen","shell execution (subprocess.Popen)"),
    ("subprocess.call", "shell execution (subprocess.call)"),
    ("subprocess.run(", "shell execution (subprocess.run)"),
    ("os.system(",      "shell execution (os.system)"),
    ("os.popen(",       "shell execution (os.popen)"),
]


def _find_blocked(code: str) -> str | None:
    """Return a description of the first blocked pattern found, or None."""
    for pattern, description in _BLOCKED_PATTERNS:
        if pattern in code:
            return description
    return None


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def execute_nuke_code(code: str) -> dict:
        """Execute arbitrary Python inside Nuke's main thread, with full access
        to the `nuke` module and the local filesystem -- code runs with the
        same permissions as the Nuke process itself. Prefer the structured
        tools (create_node, set_knob_values, etc.) when they cover what you
        need; use this only when no structured tool does.

        Certain dangerous patterns are blocked before the code reaches Nuke:
        filesystem deletion (os.remove / shutil.rmtree), process termination
        (sys.exit), and shell execution (os.system / subprocess).

        To return a value, assign it to a variable named `__result__`.
        Anything printed to stdout/stderr is also captured and returned.

        Args:
            code: Python source to execute. `nuke` is already imported in its namespace.
        """
        blocked = _find_blocked(code)
        if blocked:
            return {
                "success": False,
                "error": "blocked: code contains a disallowed pattern -- {}".format(blocked),
                "stdout": "",
                "stderr": "",
                "result": None,
            }
        return send_request("execute_nuke_code", {"code": code})
