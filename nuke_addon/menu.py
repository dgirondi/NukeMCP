"""NukeMCP addon entry point.

Nuke auto-loads this file from any directory on NUKE_PATH. Install by
adding this addon's directory (nuke_addon/) to NUKE_PATH -- see
docs/INSTALL.md.
"""

import os

import nuke

from nukemcp_server import listener

_menu = nuke.menu("Nuke").addMenu("NukeMCP")
_menu.addCommand("Start Server", listener.start_listener)
_menu.addCommand("Stop Server", listener.stop_listener)
_menu.addCommand("Status", listener.show_status)

if os.environ.get("NUKEMCP_AUTOSTART", "1") != "0":
    try:
        listener.start_listener()
    except Exception as exc:
        nuke.tprint("[NukeMCP] auto-start failed: {}".format(exc))
