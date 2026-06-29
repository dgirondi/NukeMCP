from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_script_info() -> dict:
        """Get the current Nuke script's project settings: frame range, fps,
        format, script path, and whether there are unsaved changes."""
        return send_request("get_script_info", {})
