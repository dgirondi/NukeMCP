import os

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def render(node_name: str | None, first_frame: int, last_frame: int) -> dict:
        """Render a frame range. Can legitimately take a long time for large
        ranges or heavy comps -- this call blocks until the render finishes
        or the connection times out.

        Args:
            node_name: name of a Write node to render, or None to render all
                Write nodes in the script.
            first_frame, last_frame: frame range to render (inclusive).
        """
        return send_request("render", {
            "node_name": node_name, "first_frame": first_frame, "last_frame": last_frame,
        })

    @mcp.tool()
    def get_node_screenshot(node_name: str, frame: int | None = None) -> Image:
        """Render one frame of the given node's output and return it as an image.

        Args:
            node_name: the node's name, e.g. "Blur1".
            frame: which frame to render, defaults to the current frame.
        """
        result = send_request("get_node_screenshot", {"node_name": node_name, "frame": frame})
        temp_path = result["path"]
        try:
            # Read bytes now rather than handing Image(path=...) the path: Image
            # only reads the file lazily, when the SDK serializes the tool result
            # *after* this function returns -- by which point a delete-on-return
            # would have already removed it. Reading eagerly and passing data=
            # sidesteps that timing entirely.
            with open(temp_path, "rb") as f:
                data = f.read()
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return Image(data=data, format="png")
