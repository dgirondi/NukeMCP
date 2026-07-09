from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def create_node(
        node_class: str,
        knobs: dict | None = None,
        xpos: int | None = None,
        ypos: int | None = None,
        inputs: list[str] | None = None,
    ) -> dict:
        """Create a new node in the live Nuke script. The operation is undoable.

        Args:
            node_class: Nuke node class name, e.g. "Blur", "Grade", "Write".
            knobs: optional dict of knob name -> value to set immediately after creation.
            xpos, ypos: optional position in the Node Graph.
            inputs: optional list of existing node names to wire into input 0, 1, 2... in order.
        """
        return send_request("create_node", {
            "node_class": node_class,
            "knobs": knobs or {},
            "xpos": xpos,
            "ypos": ypos,
            "inputs": inputs or [],
        })

    @mcp.tool()
    def set_knob_values(node_name: str, knobs: dict) -> dict:
        """Set one or more knob values on an existing node. Undoable.

        Args:
            node_name: the node's name, e.g. "Blur1".
            knobs: dict of knob name -> new value.
        """
        return send_request("set_knob_values", {"node_name": node_name, "knobs": knobs})

    @mcp.tool()
    def connect_nodes(from_node: str, to_node: str, input_index: int = 0) -> dict:
        """Wire from_node's output into one of to_node's inputs. Undoable.

        Args:
            from_node: name of the node supplying the output.
            to_node: name of the node receiving the connection.
            input_index: which input slot on to_node to connect (0 = first/top input).
        """
        return send_request("connect_nodes", {
            "from_node": from_node, "to_node": to_node, "input_index": input_index,
        })

    @mcp.tool()
    def delete_node(node_name: str) -> dict:
        """Delete a node from the script. Undoable.

        Args:
            node_name: the node's name, e.g. "Blur1".
        """
        return send_request("delete_node", {"node_name": node_name})

    @mcp.tool()
    def duplicate_node(
        node_name: str,
        xpos_offset: int = 100,
        ypos_offset: int = 0,
    ) -> dict:
        """Duplicate a node, preserving all knob values. Undoable.

        Args:
            node_name: name of the node to duplicate.
            xpos_offset: horizontal offset from the original node's position.
            ypos_offset: vertical offset from the original node's position.
        """
        return send_request("duplicate_node", {
            "node_name": node_name,
            "xpos_offset": xpos_offset,
            "ypos_offset": ypos_offset,
        })

    @mcp.tool()
    def list_node_classes(category: str | None = None) -> dict:
        """List available node classes from the Nodes menu, grouped by category.

        Useful for discovering what nodes can be created before calling create_node.

        Args:
            category: optional category name to filter to, e.g. "Filter" or "Color".
                      If omitted, returns all categories.
        """
        return send_request("list_node_classes", {"category": category})

    @mcp.tool()
    def get_node_default_knobs(node_class: str) -> dict:
        """Return the default knob values for a node class by creating a temporary
        node, reading its knobs, then immediately deleting it.

        Useful for inspecting what knobs a node has and what their defaults are
        before creating one for real.

        Args:
            node_class: Nuke node class name, e.g. "Blur", "Grade".
        """
        return send_request("get_node_default_knobs", {"node_class": node_class})
