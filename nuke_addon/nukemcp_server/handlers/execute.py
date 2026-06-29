import contextlib
import io

import nuke

from ..dispatch import register_handler


@register_handler("execute_nuke_code")
def execute_nuke_code(params):
    code = params["code"]
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    exec_globals = {"nuke": nuke, "__result__": None}

    success, error_message = True, None
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            exec(code, exec_globals)
    except Exception as exc:
        success, error_message = False, str(exc)

    result_value = exec_globals.get("__result__")
    if not _is_jsonable(result_value):
        result_value = str(result_value)

    return {
        "success": success,
        "error": error_message,
        "stdout": stdout_buf.getvalue(),
        "stderr": stderr_buf.getvalue(),
        "result": result_value,
    }


def _is_jsonable(value):
    if isinstance(value, (int, float, str, bool)) or value is None:
        return True
    if isinstance(value, (list, tuple)):
        return all(_is_jsonable(v) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _is_jsonable(v) for k, v in value.items())
    return False
