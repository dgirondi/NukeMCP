import os

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def render(
        node_name: str | None = None,
        first_frame: int | None = None,
        last_frame: int | None = None,
        frame_range: str | None = None,
        proxy_mode: bool = False,
    ) -> dict:
        """Render a frame range. Can legitimately take a long time for large
        ranges or heavy comps -- this call blocks until the render finishes
        or the connection times out.

        Frame range can be specified in two ways:
          - first_frame + last_frame (e.g. first_frame=1, last_frame=10)
          - frame_range string, which supports compound specs
            (e.g. "1-5,7,9-12" renders frames 1-5, then 7, then 9-12).
            frame_range takes priority if both forms are provided.

        Args:
            node_name: name of a Write node to render, or None to render all
                Write nodes in the script.
            first_frame, last_frame: simple frame range (inclusive).
            frame_range: compound frame range string, e.g. "1-10" or "1-5,7,9-12".
            proxy_mode: if True, enables Nuke proxy mode for this render only
                (useful for fast low-res previews), then restores the previous
                proxy setting.
        """
        params: dict = {"node_name": node_name, "proxy_mode": proxy_mode}
        if frame_range is not None:
            params["frame_range"] = frame_range
        elif first_frame is not None and last_frame is not None:
            params["first_frame"] = first_frame
            params["last_frame"] = last_frame
        else:
            raise ValueError("provide frame_range or both first_frame and last_frame")
        return send_request("render", params)

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
