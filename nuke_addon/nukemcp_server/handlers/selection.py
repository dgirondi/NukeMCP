import nuke

from ..dispatch import register_handler


@register_handler("get_selection")
def get_selection(params):
    return {
        "nodes": [{"name": n.name(), "class": n.Class()} for n in nuke.selectedNodes()]
    }


@register_handler("select_nodes")
def select_nodes(params):
    node_names = params["node_names"]
    additive = bool(params.get("additive", False))

    if not additive:
        for node in nuke.allNodes():
            node.setSelected(False)

    selected = []
    errors = {}
    for name in node_names:
        node = nuke.toNode(name)
        if node is None:
            errors[name] = "no such node"
            continue
        node.setSelected(True)
        selected.append(name)

    return {"selected": selected, "errors": errors}
