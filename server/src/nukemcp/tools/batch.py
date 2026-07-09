from mcp.server.fastmcp import FastMCP

from nukemcp.connection import send_request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def batch(
        operations: list[dict],
        label: str = "batch",
        stop_on_error: bool = False,
    ) -> dict:
        """Execute multiple NukeMCP tool operations as one atomic, undoable action.

        The entire batch is wrapped in a single Nuke undo group, so the artist
        can undo all changes at once with Ctrl+Z / Cmd+Z.

        Each operation is a dict with keys:
          - "tool": the tool name, e.g. "create_node"
          - "params": the params dict for that tool

        Returns a "results" list with one entry per operation, each containing
        "ok" (bool), "tool" (name), and either "result" or "message"+"error_type".

        Args:
            operations: list of {"tool": str, "params": dict} dicts to execute in order.
            label: human-readable label shown in Nuke's undo history.
            stop_on_error: if True, halt on the first failed operation.
        """
        return send_request("batch", {
            "operations": operations,
            "label": label,
            "stop_on_error": stop_on_error,
        })
