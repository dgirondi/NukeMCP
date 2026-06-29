from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def execute_nuke_code(code: str) -> dict:
        """Execute arbitrary Python inside Nuke's main thread, with full access
        to the `nuke` module and the local filesystem -- code runs with the
        same permissions as the Nuke process itself. Prefer the structured
        tools (create_node, set_knob_values, etc.) when they cover what you
        need; use this only when no structured tool does.

        To return a value, assign it to a variable named `__result__`.
        Anything printed to stdout/stderr is also captured and returned.

        Args:
            code: Python source to execute. `nuke` is already imported in its namespace.
        """
        return send_request("execute_nuke_code", {"code": code})
