"""Tool-name -> handler registry.

`handle()` is the function that actually runs ON NUKE'S MAIN THREAD -- it is
passed as the `call` argument to `nuke.executeInMainThreadWithResult` by
listener.py. Keep this module free of socket/IO concerns; those belong in
listener.py. `import nuke` (beyond this file) should only appear in
handlers/*.py.

IMPORTANT: confirmed empirically (not just from docs) that
`nuke.executeInMainThreadWithResult` does NOT propagate exceptions raised
inside the dispatched callable back to the calling thread -- Nuke's own
`executeInMain.py` wrapper catches them, prints a traceback to Nuke's
console/log, and the caller just gets back `None`. So `handle()` must
catch its own exceptions and return a plain envelope dict instead of
raising -- raising here would silently look like success-with-null-result
to whoever called executeInMainThreadWithResult.
"""

_HANDLERS = {}


def register_handler(name):
    def _decorator(func):
        _HANDLERS[name] = func
        return func
    return _decorator


def handle(request):
    tool_name = request.get("tool")
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return {"ok": False, "message": "no such tool: {!r}".format(tool_name), "error_type": "UnknownToolError"}
    try:
        result = handler(request.get("params") or {})
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "message": str(exc), "error_type": type(exc).__name__}


def _load_handlers():
    # Importing these modules triggers their @register_handler decorators.
    from .handlers import (  # noqa: F401
        execute,
        graph,
        nodes,
        render,
        script_info,
        script_io,
        selection,
    )


_load_handlers()
