"""Nmap 扫描引擎：有 nmap 二进制时真实调用，否则走模拟器"""
from __future__ import annotations

from .base import RawScanResult, ScanEngine, VulnFinding, nmap_available
from .simulator import simulate


class NmapEngine(ScanEngine):
    name = "nmap"

    def run(self, targets: list[str], config: dict | None = None) -> RawScanResult:
        config = config or self.config or {}
        ports = config.get("ports") or "1-1000"
        force_sim = config.get("simulate")
        if force_sim or not nmap_available():
            return simulate(targets, ports, self.name)
        return self._real(targets, ports)

    def _real(self, targets: list[str], ports: str) -> RawScanResult:
        import nmap  # 延迟导入：仅真实扫描时依赖 python-nmap

        scanner = nmap.PortScanner()
        scanner.scan(" ".join(targets), ports, arguments="-sV")
        raw_output = scanner.get_nmap_last_output() or ""
        findings: list[VulnFinding] = []
        for host in scanner.all_hosts():
            for proto in scanner[host].all_protocols():
                for port in scanner[host][proto].keys():
                    svc = scanner[host][proto][port]
                    if svc.get("state") != "open":
                        continue
                    name = svc.get("name", "unknown")
                    product = svc.get("product", "")
                    version = svc.get("version", "")
                    findings.append(VulnFinding(
                        name=f"{name} 服务开放（{host}）",
                        risk_level="low",
                        description=f"在 {host}:{port}/{proto} 发现服务 {name} {version}。",
                        vuln_type="exposure",
                        port=str(port),
                        protocol=proto,
                        component=product or name,
                        version=version,
                        service=name,
                        target=host,
                    ))
        return RawScanResult(engine=self.name, targets=targets, raw_output=raw_output, findings=findings)
