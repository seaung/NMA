"""扫描引擎工厂：按名称获取引擎实例"""
from __future__ import annotations

from .base import ScanEngine
from .nmap import NmapEngine
from .stub import AwvsEngine, NessusEngine

_ENGINES = {
    "nmap": NmapEngine,
    "nessus": NessusEngine,
    "awvs": AwvsEngine,
    "custom": NmapEngine,
}


def get_engine(name: str, config: dict | None = None) -> ScanEngine:
    cls = _ENGINES.get(name, NmapEngine)
    return cls(config or {})
