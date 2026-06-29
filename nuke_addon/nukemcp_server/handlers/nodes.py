import nuke

from ..dispatch import register_handler
from .graph import _node_summary


def _require_node(node_name):
    node = nuke.toNode(node_name)
    if node is None:
        raise LookupError("no such node: {!r}".format(node_name))
    return node


def _apply_knobs(node, knobs):
    applied = []
    errors = {}
    for knob_name, value in (knobs or {}).items():
        knob = node.knob(knob_name)
        if knob is None:
            errors[knob_name] = "no such knob"
            continue
        try:
            knob.setValue(value)
            applied.append(knob_name)
        except Exception as exc:
            errors[knob_name] = str(exc)
    return applied, errors


@register_handler("create_node")
def create_node(params):
    node_class = params["node_class"]
    node = nuke.createNode(node_class, inpanel=False)

    xpos = params.get("xpos")
    ypos = params.get("ypos")
    if xpos is not None:
        node.setXpos(int(xpos))
    if ypos is not None:
        node.setYpos(int(ypos))

    applied, knob_errors = _apply_knobs(node, params.get("knobs"))

    input_errors = {}
    for index, input_name in enumerate(params.get("inputs") or []):
        input_node = nuke.toNode(input_name)
        if input_node is None:
            input_errors[str(index)] = "no such node: {!r}".format(input_name)
            continue
        node.setInput(index, input_node)

    result = _node_summary(node)
    result["knobs_applied"] = applied
    result["knob_errors"] = knob_errors
    result["input_errors"] = input_errors
    return result


@register_handler("set_knob_values")
def set_knob_values(params):
    node = _require_node(params["node_name"])
    applied, errors = _apply_knobs(node, params.get("knobs"))
    return {"node_name": node.name(), "knobs_applied": applied, "errors": errors}


@register_handler("connect_nodes")
def connect_nodes(params):
    from_node = _require_node(params["from_node"])
    to_node = _require_node(params["to_node"])
    input_index = int(params.get("input_index", 0))
    to_node.setInput(input_index, from_node)
    return {"from_node": from_node.name(), "to_node": to_node.name(), "input_index": input_index}


@register_handler("delete_node")
def delete_node(params):
    node = _require_node(params["node_name"])
    name = node.name()
    nuke.delete(node)
    return {"deleted": name}
