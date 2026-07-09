from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
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
