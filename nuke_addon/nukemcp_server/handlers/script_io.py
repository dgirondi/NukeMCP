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
