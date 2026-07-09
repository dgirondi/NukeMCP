import os
import tempfile

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

    with nuke.UndoGroup("NukeMCP: create_node"):
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
    with nuke.UndoGroup("NukeMCP: set_knob_values"):
        applied, errors = _apply_knobs(node, params.get("knobs"))
    return {"node_name": node.name(), "knobs_applied": applied, "errors": errors}


@register_handler("connect_nodes")
def connect_nodes(params):
    from_node = _require_node(params["from_node"])
    to_node = _require_node(params["to_node"])
    input_index = int(params.get("input_index", 0))
    with nuke.UndoGroup("NukeMCP: connect_nodes"):
        to_node.setInput(input_index, from_node)
    return {"from_node": from_node.name(), "to_node": to_node.name(), "input_index": input_index}


@register_handler("delete_node")
def delete_node(params):
    node = _require_node(params["node_name"])
    name = node.name()
    with nuke.UndoGroup("NukeMCP: delete_node"):
        nuke.delete(node)
    return {"deleted": name}


@register_handler("duplicate_node")
def duplicate_node(params):
    """Duplicate a node via script copy/paste, preserving all knob values."""
    original = _require_node(params["node_name"])
    xpos_offset = int(params.get("xpos_offset", 100))
    ypos_offset = int(params.get("ypos_offset", 0))

    with nuke.UndoGroup("NukeMCP: duplicate_node"):
        # Save current selection; work with a clean slate
        prev_selected = [n for n in nuke.allNodes() if n.isSelected()]
        for n in prev_selected:
            n.setSelected(False)

        original.setSelected(True)

        fd, tmp = tempfile.mkstemp(suffix=".nk")
        os.close(fd)
        try:
            nuke.nodeCopy(tmp)
            original.setSelected(False)
            nuke.nodePaste(tmp)
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass

        new_nodes = nuke.selectedNodes()
        orig_x, orig_y = original.xpos(), original.ypos()
        for new_node in new_nodes:
            new_node.setXpos(orig_x + xpos_offset)
            new_node.setYpos(orig_y + ypos_offset)

        # Restore original selection
        for n in nuke.allNodes():
            n.setSelected(False)
        for n in prev_selected:
            try:
                n.setSelected(True)
            except Exception:
                pass

    if not new_nodes:
        raise RuntimeError("duplicate produced no new nodes")

    return _node_summary(new_nodes[0])


@register_handler("list_node_classes")
def list_node_classes(params):
    """Walk the Nodes menu to return available node classes grouped by category."""
    category_filter = params.get("category")

    nodes_menu = nuke.menu("Nodes")
    result = {}

    for top_item in nodes_menu.items():
        cat_name = top_item.name()
        if not cat_name or cat_name.startswith("-"):
            continue
        try:
            sub_items = top_item.items()
        except AttributeError:
            # Leaf at top level; rare but include it
            result.setdefault("_top", []).append(cat_name)
            continue

        classes = []
        for sub_item in sub_items:
            name = sub_item.name()
            if not name or name.startswith("-"):
                continue
            try:
                # If this item also has children it's a sub-category;
                # include those class names too, prefixed with the sub-category.
                sub_sub = sub_item.items()
                for leaf in sub_sub:
                    lname = leaf.name()
                    if lname and not lname.startswith("-"):
                        classes.append("{}/{}".format(name, lname))
            except AttributeError:
                classes.append(name)

        if classes:
            result[cat_name] = sorted(classes)

    if category_filter:
        return {
            "category": category_filter,
            "classes": result.get(category_filter, []),
        }

    return {
        "categories": result,
        "total_classes": sum(len(v) for v in result.values()),
    }


@register_handler("get_node_default_knobs")
def get_node_default_knobs(params):
    """Create a temporary node of the given class, read its default knobs, then delete it."""
    from .knob_serialization import serialize_all_knobs

    node_class = params["node_class"]

    # Run inside an undo group so this transient creation can be undone if needed
    with nuke.UndoGroup("NukeMCP: get_node_default_knobs"):
        node = nuke.createNode(node_class, inpanel=False)
        try:
            knobs = serialize_all_knobs(node)
        finally:
            nuke.delete(node)

    return {"node_class": node_class, "knobs": knobs}
