import nuke

from ..dispatch import register_handler


@register_handler("get_node_errors")
def get_node_errors(params):
    """Return all nodes that currently have errors."""
    recurse_groups = bool(params.get("recurse_groups", False))

    try:
        all_nodes = nuke.allNodes(recurseGroups=recurse_groups)
    except TypeError:
        all_nodes = nuke.allNodes()

    errors = []
    for node in all_nodes:
        try:
            err = node.error()
            if err:
                # node.error() returns a non-empty string when there is an error
                msg = str(err) if isinstance(err, str) else ""
                if not msg:
                    try:
                        msg = str(node.message())
                    except Exception:
                        pass
                errors.append({
                    "name": node.name(),
                    "class": node.Class(),
                    "message": msg,
                })
        except Exception:
            pass

    return {"errors": errors, "count": len(errors)}


@register_handler("get_node_metadata")
def get_node_metadata(params):
    """Return the embedded image metadata from a node (most useful on Read nodes)."""
    node_name = params["node_name"]
    frame = params.get("frame")

    node = nuke.toNode(node_name)
    if node is None:
        raise LookupError("no such node: {!r}".format(node_name))

    actual_frame = int(frame) if frame is not None else int(nuke.frame())

    try:
        metadata = node.metadata(time=actual_frame)
    except TypeError:
        # Some Nuke versions don't accept 'time' kwarg
        try:
            metadata = node.metadata()
        except Exception as exc:
            return {"node": node_name, "frame": actual_frame, "metadata": {}, "error": str(exc)}
    except Exception as exc:
        return {"node": node_name, "frame": actual_frame, "metadata": {}, "error": str(exc)}

    # Ensure all values are JSON-serializable
    safe = {}
    for k, v in (metadata or {}).items():
        try:
            import json
            json.dumps(v)
            safe[k] = v
        except (TypeError, ValueError):
            safe[k] = str(v)

    return {"node": node_name, "frame": actual_frame, "metadata": safe}
