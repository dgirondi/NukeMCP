from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def create_viewer(
        connect_to: str | None = None,
        xpos: int | None = None,
        ypos: int | None = None,
    ) -> dict:
        """Create a Viewer node in the script, optionally connected to an existing node.

        Useful for session setup: after creating a node graph, call this once
        to add a viewer and wire it to the final output node.

        Args:
            connect_to: optional node name to connect to the Viewer's input.
            xpos, ypos: optional position in the Node Graph.
        """
        return send_request("create_viewer", {
            "connect_to": connect_to,
            "xpos": xpos,
            "ypos": ypos,
        })

    @mcp.tool()
    def get_viewer_node() -> dict:
        """Get info about the currently active Viewer node: what it's connected
        to, the current frame, and gain/gamma settings."""
        return send_request("get_viewer_node", {})

    @mcp.tool()
    def set_viewer_input(node_name: str, input_index: int = 0) -> dict:
        """Connect a node to a Viewer input so it becomes visible on screen.

        Args:
            node_name: the node whose output to display in the Viewer.
            input_index: which Viewer input to connect to (0 = A, 1 = B).
        """
        return send_request("set_viewer_input", {
            "node_name": node_name,
            "input_index": input_index,
        })

    @mcp.tool()
    def zoom_to_node(node_name: str) -> dict:
        """Pan and zoom the Node Graph so the given node is centred on screen.

        Args:
            node_name: name of the node to centre on.
        """
        return send_request("zoom_to_node", {"node_name": node_name})

    @mcp.tool()
    def viewer_playback(action: str, frame: int | None = None) -> dict:
        """Control Viewer playback or navigate the timeline.

        Actions:
          - "play" / "forward": start forward playback.
          - "backward": start reverse playback.
          - "stop": halt playback.
          - "next": advance one frame.
          - "prev": step back one frame.
          - "goto": jump to a specific frame (requires the `frame` argument).

        Continuous play/stop relies on Nuke 13+ ViewerWindow API. Frame stepping
        and goto always work regardless of Nuke version.

        Args:
            action: one of play, stop, next, prev, goto, forward, backward.
            frame: destination frame for the "goto" action.
        """
        params: dict = {"action": action}
        if frame is not None:
            params["frame"] = frame
        return send_request("viewer_playback", params)
