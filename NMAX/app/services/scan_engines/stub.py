"""Nessus / AWVS 适配占位引擎：MVP 阶段复用模拟器，预留真实 API 接入"""
from __future__ import annotations

from .base import RawScanResult, ScanEngine
from .simulator import simulate


class StubEngine(ScanEngine):
    name = "stub"

    def run(self, targets: list[str], config: dict | None = None) -> RawScanResult:
        config = config or self.config or {}
        ports = config.get("ports") or "1-1000"
        return simulate(targets, ports, self.name)


class NessusEngine(StubEngine):
    name = "nessus"


class AwvsEngine(StubEngine):
    name = "awvs"
