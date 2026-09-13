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
class ProtocolProvider:
    def __init__(self, *args, **kwargs):
        del args, kwargs


base.ProtocolProvider = ProtocolProvider
credential_guard.get_adapter_credential_status = lambda _name, config: {
    "configured": bool((config or {}).get("username") and (config or {}).get("password")),
    "missing_fields": [],
}
protocol.base = base
protocol.credential_guard = credential_guard
sys.modules.setdefault("protocol", protocol)
sys.modules.setdefault("protocol.base", base)
sys.modules.setdefault("protocol.credential_guard", credential_guard)

logger = types.ModuleType("infrastructure.logger")
logger.error_logger = types.SimpleNamespace(error=lambda *args, **kwargs: None)
infrastructure = types.ModuleType("infrastructure")
infrastructure.logger = logger
sys.modules.setdefault("infrastructure", infrastructure)
sys.modules.setdefault("infrastructure.logger", logger)
