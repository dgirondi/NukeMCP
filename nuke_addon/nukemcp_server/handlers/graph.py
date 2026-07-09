import nuke

from ..dispatch import register_handler
from .knob_serialization import serialize_all_knobs


def _iter_nodes(filter_class, recurse_groups=False):
    try:
        if filter_class:
            nodes = nuke.allNodes(filter_class, recurseGroups=recurse_groups)
        else:
            nodes = nuke.allNodes(recurseGroups=recurse_groups)
    except TypeError:
        # Older Nuke builds that don't accept recurseGroups
        nodes = nuke.allNodes(filter_class) if filter_class else nuke.allNodes()
    for node in nodes:
        yield node


def _node_summary(node):
    return {
        "name": node.name(),
        "class": node.Class(),
        "xpos": node.xpos(),
        "ypos": node.ypos(),
        "selected": node.isSelected(),
    }


@register_handler("list_nodes")
def list_nodes(params):
    filter_class = params.get("filter_class")
    recurse_groups = bool(params.get("recurse_groups", False))
    return {"nodes": [_node_summary(n) for n in _iter_nodes(filter_class, recurse_groups)]}


@register_handler("get_node_graph")
def get_node_graph(params):
    filter_class = params.get("filter_class")
    recurse_groups = bool(params.get("recurse_groups", False))
    nodes = []
    for node in _iter_nodes(filter_class, recurse_groups):
        summary = _node_summary(node)
        inputs = []
        for i in range(node.inputs()):
            input_node = node.input(i)
            inputs.append(input_node.name() if input_node else None)
        summary["inputs"] = inputs
        try:
            summary["outputs"] = [n.name() for n in node.dependent()]
        except Exception:
            summary["outputs"] = []
        nodes.append(summary)
    return {"nodes": nodes}


@register_handler("get_node_info")
def get_node_info(params):
    node_name = params["node_name"]
    node = nuke.toNode(node_name)
    if node is None:
        raise LookupError("no such node: {!r}".format(node_name))
    info = _node_summary(node)
    info["knobs"] = serialize_all_knobs(node)
    return info
