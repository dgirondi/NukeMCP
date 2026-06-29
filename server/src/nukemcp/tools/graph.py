from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def list_nodes(filter_class: str | None = None) -> dict:
        """List all nodes in the current script (name, class, position, selection state).

        Args:
            filter_class: optional Nuke node class name, e.g. "Blur", to only list nodes of that class.
        """
        return send_request("list_nodes", {"filter_class": filter_class})

    @mcp.tool()
    def get_node_graph(filter_class: str | None = None) -> dict:
        """Like list_nodes, but also includes each node's input/output connections by name.

        Args:
            filter_class: optional Nuke node class name to only include nodes of that class.
        """
        return send_request("get_node_graph", {"filter_class": filter_class})

    @mcp.tool()
    def get_node_info(node_name: str) -> dict:
        """Get full detail for one node: class, position, selection state, and every
        knob's value. Knob values that are animated or expression-driven are flagged
        as such (the reported value is just the value at the current frame).

        Args:
            node_name: the node's name, e.g. "Blur1".
        """
        return send_request("get_node_info", {"node_name": node_name})
