"""Windows compatibility shim for gltest direct mode."""
import os
_unlink, _pending = os.unlink, []
def _safe(path, *args, **kwargs):
    try: return _unlink(path, *args, **kwargs)
    except PermissionError: _pending.append(path)
if os.name == "nt": os.unlink = _safe
def pytest_sessionfinish(session, exitstatus):
    if os.name != "nt": return
    os.unlink = _unlink
    for path in _pending:
        try: _unlink(path)
        except OSError: pass
