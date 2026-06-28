from __future__ import annotations

try:
    from core.soul_map_engine import EVOLUTION_STAGES, SoulMapEngine
except ImportError:
    from apps.truth_api.core.soul_map_engine import EVOLUTION_STAGES, SoulMapEngine


__all__ = ["EVOLUTION_STAGES", "SoulMapEngine"]
