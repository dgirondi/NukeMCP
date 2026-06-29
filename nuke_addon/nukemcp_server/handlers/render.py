import contextlib
import io
import os
import tempfile

import nuke

from ..dispatch import register_handler


@register_handler("render")
def render(params):
    node_name = params.get("node_name")
    first_frame = int(params["first_frame"])
    last_frame = int(params["last_frame"])

    if node_name:
        node = nuke.toNode(node_name)
        if node is None:
            raise LookupError("no such node: {!r}".format(node_name))
        targets = node
    else:
        targets = nuke.allNodes("Write")
        if not targets:
            raise ValueError("no node_name given and no Write nodes exist in the script")

    # nuke.execute()'s own exception is the authoritative success/failure signal.
    # Captured stdout/stderr is best-effort supplementary info -- Nuke's render
    # engine may log via its own path rather than Python's sys.stdout, so don't
    # rely on an empty buffer to mean "no warnings."
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    success, error_message = True, None
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            nuke.execute(targets, first_frame, last_frame)
    except Exception as exc:
        success, error_message = False, str(exc)

    return {
        "success": success,
        "error": error_message,
        "stdout": stdout_buf.getvalue(),
        "stderr": stderr_buf.getvalue(),
        "first_frame": first_frame,
        "last_frame": last_frame,
    }


@register_handler("get_node_screenshot")
def get_node_screenshot(params):
    node_name = params["node_name"]
    node = nuke.toNode(node_name)
    if node is None:
        raise LookupError("no such node: {!r}".format(node_name))

    frame = params.get("frame")
    frame = int(frame) if frame is not None else int(nuke.frame())

    fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="nukemcp_")
    os.close(fd)

    write_node = nuke.createNode("Write", inpanel=False)
    try:
        write_node.setInput(0, node)
        write_node["file"].setValue(temp_path)
        nuke.execute(write_node, frame, frame)
    finally:
        nuke.delete(write_node)

    return {"path": temp_path, "frame": frame}
