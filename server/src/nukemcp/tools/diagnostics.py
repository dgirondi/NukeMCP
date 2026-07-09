from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_node_errors(recurse_groups: bool = False) -> dict:
        """Return every node in the script that currently has an error.

        Args:
            recurse_groups: if True, also inspect nodes inside Group nodes.
        """
        return send_request("get_node_errors", {"recurse_groups": recurse_groups})

    @mcp.tool()
    def get_node_metadata(node_name: str, frame: int | None = None) -> dict:
        """Return the embedded image metadata from a node's output (most
        useful on Read nodes — gives you colorspace, format, camera info,
        custom EXR metadata, etc.).

        Args:
            node_name: name of the node, e.g. "Read1".
            frame: frame to sample metadata at; defaults to the current frame.
        """
        return send_request("get_node_metadata", {"node_name": node_name, "frame": frame})
