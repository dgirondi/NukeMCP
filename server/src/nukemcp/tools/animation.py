from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def set_knob_expression(
        node_name: str,
        knob_name: str,
        expression: str,
        field_index: int | None = None,
    ) -> dict:
        """Set a Nuke expression on a knob. Pass an empty string to clear the
        expression and return the knob to a static value.

        Args:
            node_name: name of the node, e.g. "Transform1".
            knob_name: name of the knob, e.g. "translate".
            expression: Nuke expression string, e.g. "frame * 2". Empty string clears.
            field_index: for multi-field knobs (e.g. Color), which field to set (0-based).
        """
        return send_request("set_knob_expression", {
            "node_name": node_name,
            "knob_name": knob_name,
            "expression": expression,
            "field_index": field_index,
        })

    @mcp.tool()
    def set_knob_keyframe(
        node_name: str,
        knob_name: str,
        frame: float,
        value: float,
        field_index: int | None = None,
    ) -> dict:
        """Set an animation keyframe on a knob at a specific frame.

        Args:
            node_name: name of the node, e.g. "Transform1".
            knob_name: name of the knob, e.g. "rotate".
            frame: the frame number to set the keyframe at.
            value: the value to set at that frame.
            field_index: for multi-field knobs, which field to animate (0-based).
        """
        return send_request("set_knob_keyframe", {
            "node_name": node_name,
            "knob_name": knob_name,
            "frame": frame,
            "value": value,
            "field_index": field_index,
        })

    @mcp.tool()
    def remove_knob_animation(
        node_name: str,
        knob_name: str,
        field_index: int | None = None,
    ) -> dict:
        """Remove all animation curves and expressions from a knob, leaving its
        current evaluated value as a static constant.

        Args:
            node_name: name of the node.
            knob_name: name of the knob.
            field_index: for multi-field knobs, which field to clear (omit for all).
        """
        return send_request("remove_knob_animation", {
            "node_name": node_name,
            "knob_name": knob_name,
            "field_index": field_index,
        })
