import nuke

from ..dispatch import register_handler


@register_handler("get_script_info")
def get_script_info(params):
    root = nuke.root()
    fmt = root["format"].value()
    return {
        "script_path": root.name(),
        "modified": root.modified(),
        "first_frame": int(root["first_frame"].value()),
        "last_frame": int(root["last_frame"].value()),
        "fps": root["fps"].value(),
        "format": {
            "name": fmt.name(),
            "width": fmt.width(),
            "height": fmt.height(),
        },
    }
