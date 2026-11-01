"""扫描引擎抽象层：统一 RawScanResult / VulnFinding 数据结构与接口"""
from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VulnFinding:
    """单个漏洞发现（与引擎无关）"""

    name: str
    risk_level: str = "medium"
    description: str = ""
    cve_id: str | None = None
    cvss_score: float | None = None
    vuln_type: str = "exposure"
    solution: str = ""
    port: str = ""
    protocol: str = ""
    component: str = ""
    version: str = ""
    service: str = ""
    target: str = ""  # 来源目标（IP / 域名 / URL）


@dataclass
class RawScanResult:
    engine: str
    targets: list[str]
    raw_output: str = ""
    findings: list[VulnFinding] = field(default_factory=list)


class ScanEngine(ABC):
    """扫描引擎统一接口：run 返回标准化结果，parse 可选单独解析"""

    name: str = ""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    @abstractmethod
    def run(self, targets: list[str], config: dict | None = None) -> RawScanResult:
        ...


def nmap_available() -> bool:
    """检测本机是否存在 nmap 二进制；不存在时引擎自动走模拟模式。"""
    return shutil.which("nmap") is not None
