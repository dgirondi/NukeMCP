from mcp.server.fastmcp import FastMCP

from nukemcp.tools import register_all


def main() -> int:
    mcp = FastMCP(
        "nukemcp",
        instructions=(
            "Tools for inspecting and controlling a running Nuke 17 session. "
            "Requires Nuke to be open with the NukeMCP addon's listener started "
            "(Nuke menu: NukeMCP > Start Server)."
        ),
    )
    register_all(mcp)
    mcp.run()
    return 0
