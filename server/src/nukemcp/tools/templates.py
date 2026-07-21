from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def create_workflow_template(
        template_type: str,
        connect_to: str | None = None,
        xpos: int = 0,
        ypos: int = 0,
        add_backdrop: bool = True,
    ) -> dict:
        """Instantiate a complete, pre-wired compositing subgraph from a named
        recipe. All nodes are created, connected, labelled, and (optionally)
        wrapped in a colour-coded BackdropNode in a single undoable operation.

        Available templates:
          keying           — Keyer → Unpremult → Grade (despill) → Premult → EdgeBlur
          color_correction — Unpremult → Grade (overall/shadows/highlights) → Premult
          lens_distortion  — LensDistortion (undistort) → NoOp → LensDistortion (redistort)
          3d_simple        — Camera + Card → Scene → ScanlineRender

        Args:
            template_type: one of "keying", "color_correction", "lens_distortion",
                           "3d_simple".
            connect_to: optional existing node whose output feeds the template's
                        first input (Card for 3d_simple, first node otherwise).
            xpos, ypos: position in the Node Graph for the top of the subgraph.
            add_backdrop: wrap the created nodes in a labelled BackdropNode.
        """
        return send_request("create_workflow_template", {
            "template_type": template_type,
            "connect_to": connect_to,
            "xpos": xpos,
            "ypos": ypos,
            "add_backdrop": add_backdrop,
        })
