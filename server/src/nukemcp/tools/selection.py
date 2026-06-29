from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_selection() -> dict:
        """Get the nodes currently selected in the Nuke Node Graph.

        Reflects live selection state at call time -- this can change between
        calls, including from a human artist clicking around in the Nuke UI
        concurrently.
        """
        return send_request("get_selection", {})

    @mcp.tool()
    def select_nodes(node_names: list[str], additive: bool = False) -> dict:
        """Set which nodes are selected in the Node Graph.

        Args:
            node_names: names of nodes to select.
            additive: if False (default), clears the existing selection first.
        """
        return send_request("select_nodes", {"node_names": node_names, "additive": additive})
