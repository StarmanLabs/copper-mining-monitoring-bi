from contextlib import contextmanager
import os
import shutil
import stat
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PYTEST_TMP = ROOT / ".pytest_tmp"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _remove_tree(path: Path) -> None:
    """Remove a tree and clear write protection on Windows if needed."""
    if not path.exists():
        return

    def _onerror(func, failing_path, exc_info):
        try:
            os.chmod(failing_path, stat.S_IWRITE)
            func(failing_path)
        except OSError:
            pass

    shutil.rmtree(path, onerror=_onerror)


@contextmanager
def scratch_output_dir(name: str):
    """Create a disposable workspace-local output directory for tests."""
    PYTEST_TMP.mkdir(parents=True, exist_ok=True)
    path = PYTEST_TMP / f"{name}-{uuid4().hex[:8]}"
    _remove_tree(path)
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        _remove_tree(path)
