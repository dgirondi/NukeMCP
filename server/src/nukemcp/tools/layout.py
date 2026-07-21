from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def organize_node_graph(selected_only: bool = False) -> dict:
        """Automatically organise the node graph into labelled, coloured backdrop lanes.

        Nodes are sorted into categories — INPUTS, PREP, KEY, COLOR, FX, MERGE,
        OUTPUT, MISC — and repositioned into parallel vertical columns, one per
        populated category. A coloured BackdropNode is placed behind each column.

        BackdropNodes, Dots, and StickyNotes are left untouched.

        This operation is undoable (single Cmd+Z restores original positions).

        Args:
            selected_only: if True, only reorganise the currently selected nodes.
                           Defaults to False (reorganise every node in the script).
        """
        return send_request("organize_node_graph", {"selected_only": selected_only})
