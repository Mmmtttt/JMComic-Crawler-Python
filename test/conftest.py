from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "lib", ROOT / "lib" / "src"):
    sys.path.insert(0, str(path))

protocol = types.ModuleType("protocol")
base = types.ModuleType("protocol.base")
credential_guard = types.ModuleType("protocol.credential_guard")
base.ProtocolProvider = object
credential_guard.get_adapter_credential_status = lambda _name, config: {
    "configured": bool((config or {}).get("username") and (config or {}).get("password")),
    "missing_fields": [],
}
protocol.base = base
protocol.credential_guard = credential_guard
sys.modules.setdefault("protocol", protocol)
sys.modules.setdefault("protocol.base", base)
sys.modules.setdefault("protocol.credential_guard", credential_guard)
