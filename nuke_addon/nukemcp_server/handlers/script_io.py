import os

import nuke

from ..dispatch import register_handler


def _require_absolute(path):
    if not os.path.isabs(path):
        raise ValueError("path must be absolute: {!r}".format(path))


@register_handler("open_script")
def open_script(params):
    path = params["path"]
    _require_absolute(path)
    # nuke.scriptOpen() always opens a NEW script containing the named file's
    # contents -- it replaces the current session by itself, there's no
    # separate "merge" behavior to opt out of.
    nuke.scriptOpen(path)
    return {"opened": path}


@register_handler("save_script")
def save_script(params):
    path = params["path"]
    _require_absolute(path)
    overwrote_existing = os.path.exists(path)
    nuke.scriptSaveAs(path, overwrite=1)
    return {"saved": path, "overwrote_existing": overwrote_existing}


@register_handler("merge_script")
def merge_script(params):
    """Import nodes from another .nk file into the current script without replacing it."""
    path = params["path"]
    _require_absolute(path)
    if not os.path.exists(path):
        raise FileNotFoundError("script not found: {!r}".format(path))

    nodes_before = {n.name() for n in nuke.allNodes()}

    with nuke.UndoGroup("NukeMCP: merge_script"):
        nuke.scriptReadFile(path)

    nodes_after = {n.name() for n in nuke.allNodes()}
    new_node_names = sorted(nodes_after - nodes_before)

    return {
        "merged": path,
        "new_nodes": new_node_names,
        "count": len(new_node_names),
    }
