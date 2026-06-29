"""Per-knob JSON serialization.

`knob.value()` returns wildly different Python types depending on knob
class (float, tuple, str, a nuke.Format object, ...) and for an animated
or expression-driven knob it silently returns only the value evaluated at
the current frame, hiding the fact that it's animated. Confirmed via
Nuke's own docs (PythonDevGuide/Nuke/animation.html) that the correct way
to detect this is `knob.isAnimated()` (true for animation OR expressions)
and `knob.hasExpression()` (true specifically for expressions) -- so we
report those alongside the evaluated value instead of collapsing
everything to a bare `.value()` call.
"""

import nuke


def serialize_knob(knob):
    try:
        value = knob.value()
    except Exception as exc:
        return {"value": None, "error": str(exc), "animated": False, "expression": None}

    value = _to_jsonable(value)

    animated = False
    expression = None
    try:
        animated = bool(knob.isAnimated())
        if knob.hasExpression():
            # toScript() reflects the current expression text for single-field
            # knobs; for array knobs, fall back to a generic marker rather than
            # guessing which field holds the expression.
            try:
                expression = knob.toScript(False)
            except Exception:
                expression = True
    except (AttributeError, NameError):
        pass  # not every knob subclass supports animation (e.g. Tab_Knob)

    return {"value": value, "animated": animated, "expression": expression}


def _to_jsonable(value):
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "name"):
        # nuke.Format and similar objects expose .name()
        try:
            return value.name()
        except Exception:
            pass
    return str(value)


def serialize_all_knobs(node):
    result = {}
    for name, knob in node.knobs().items():
        result[name] = serialize_knob(knob)
    return result
