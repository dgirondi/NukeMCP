from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_script_info() -> dict:
        """Get the current Nuke script's project settings: frame range, fps,
        format, script path, and whether there are unsaved changes."""
        return send_request("get_script_info", {})

    @mcp.tool()
    def set_project_settings(
        first_frame: int | None = None,
        last_frame: int | None = None,
        fps: float | None = None,
        format: str | None = None,
        current_frame: int | None = None,
    ) -> dict:
        """Set one or more top-level project settings on the Nuke Root node. Undoable.

        Only the parameters you provide are changed; omitted ones are left as-is.

        Args:
            first_frame: start of the frame range.
            last_frame: end of the frame range.
            fps: frames per second, e.g. 23.976 or 24.0.
            format: format name or "WIDTHxHEIGHT" string, e.g. "HD_1080" or "1920x1080".
            current_frame: move the playhead to this frame (same as viewer_playback goto).
        """
        params: dict = {}
        if first_frame is not None:
            params["first_frame"] = first_frame
        if last_frame is not None:
            params["last_frame"] = last_frame
        if fps is not None:
            params["fps"] = fps
        if format is not None:
            params["format"] = format
        if current_frame is not None:
            params["current_frame"] = current_frame
        return send_request("set_project_settings", params)
