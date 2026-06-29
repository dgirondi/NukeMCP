import sys
import pathlib

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
for _path in (_REPO_ROOT / "server" / "src", _REPO_ROOT / "tests" / "fixtures"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
