import importlib
import pkgutil

from mcp.server.fastmcp import FastMCP


def register_all(mcp: FastMCP) -> None:
    for _importer, modname, _ispkg in pkgutil.iter_modules(__path__):
        mod = importlib.import_module("{}.{}".format(__name__, modname))
        if hasattr(mod, "register"):
            mod.register(mcp)
