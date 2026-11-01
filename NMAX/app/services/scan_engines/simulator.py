"""通用扫描结果模拟器：本机无 nmap / Nessus / AWVS 时生成可信的演示结果"""
from __future__ import annotations

import hashlib
import random

from .base import RawScanResult, VulnFinding

# 端口 -> 服务名（用于模拟原始输出）
SERVICE_NAME = {
    21: "ftp", 22: "ssh", 23: "telnet", 53: "domain",
    80: "http", 443: "https", 445: "microsoft-ds", 1433: "ms-sql-s",
    3306: "mysql", 3389: "ms-wbt-server", 6379: "redis",
    8080: "http-proxy", 8443: "https-alt",
}

# 端口 -> 关联风险发现（命中开放端口时按概率产出）
PORT_FINDINGS = {
    22: {
        "name": "OpenSSH 版本信息泄露", "risk_level": "low",
        "vuln_type": "information_disclosure", "component": "OpenSSH",
        "solution": "隐藏 SSH 版本号或升级到最新稳定版本。",
    },
    23: {
        "name": "Telnet 明文传输协议开放", "risk_level": "medium",
        "vuln_type": "weak_encryption", "component": "Telnet",
        "solution": "停用 Telnet，改用 SSH 进行远程管理。",
    },
    80: {
        "name": "HTTP 服务缺失安全响应头", "risk_level": "low",
        "vuln_type": "configuration", "component": "Web Server",
        "solution": "配置 CSP / HSTS / X-Frame-Options 等安全响应头。",
    },
    443: {
        "name": "TLS 协议版本过低（支持 TLS 1.0/1.1）", "risk_level": "medium",
        "vuln_type": "weak_crypto", "component": "TLS",
        "solution": "禁用 TLS 1.0/1.1，仅启用 TLS 1.2/1.3。",
    },
    445: {
        "name": "SMB 服务开放（潜在 EternalBlue 风险）", "risk_level": "high",
        "vuln_type": "remote_code_execution", "component": "Microsoft SMB",
        "cve_id": "CVE-2017-0144", "cvss_score": 8.1,
        "solution": "及时安装 MS17-010 补丁，并限制 445 端口公网暴露。",
    },
    3306: {
        "name": "MySQL 版本信息泄露", "risk_level": "low",
        "vuln_type": "information_disclosure", "component": "MySQL",
        "solution": "限制数据库端口访问并关闭版本回显。",
    },
    6379: {
        "name": "Redis 未授权访问", "risk_level": "medium",
        "vuln_type": "auth_bypass", "component": "Redis",
        "cve_id": "CVE-2022-0543", "cvss_score": 7.5,
        "solution": "为 Redis 配置访问密码并限制绑定地址。",
    },
    8080: {
        "name": "Apache Log4j 远程代码执行", "risk_level": "critical",
        "vuln_type": "remote_code_execution", "component": "Apache Log4j",
        "cve_id": "CVE-2021-44228", "cvss_score": 9.8,
        "solution": "升级 Log4j 至 2.17.1 及以上版本。",
    },
}


def simulate(targets: list[str], ports: str, engine_name: str) -> RawScanResult:
    """基于目标内容生成稳定的模拟扫描结果（同目标结果可复现）。"""
    raw_lines: list[str] = [
        f"# {engine_name} simulated scan report",
        f"# targets: {', '.join(targets)}",
        f"# ports: {ports}",
    ]
    findings: list[VulnFinding] = []

    candidate_ports = list(SERVICE_NAME.keys())
    for target in targets:
        seed = hashlib.md5(target.encode("utf-8")).hexdigest()
        rng = random.Random(seed)
        open_ports = sorted(rng.sample(candidate_ports, k=rng.randint(3, 6)))
        raw_lines.append(f"\nNmap scan report for {target}")
        raw_lines.append(f"Host is up. {len(open_ports)} ports open.")
        for p in open_ports:
            raw_lines.append(f"  {p}/tcp open {SERVICE_NAME[p]}")

        for p in open_ports:
            spec = PORT_FINDINGS.get(p)
            if spec and rng.random() < 0.75:
                findings.append(VulnFinding(
                    name=spec["name"],
                    risk_level=spec["risk_level"],
                    description=f"在目标 {target} 的 {p}/tcp 服务上发现：{spec['name']}。",
                    cve_id=spec.get("cve_id"),
                    cvss_score=spec.get("cvss_score"),
                    vuln_type=spec["vuln_type"],
                    solution=spec["solution"],
                    port=str(p),
                    protocol="tcp",
                    component=spec["component"],
                    service=SERVICE_NAME[p],
                    target=target,
                ))

    if not findings:
        # 兜底：至少一个信息类发现
        findings.append(VulnFinding(
            name="资产暴露面探测完成", risk_level="info",
            description="未发现明显可利用风险，已记录开放端口与服务指纹。",
            vuln_type="exposure", port="", protocol="", component="", target=targets[0],
        ))

    raw_lines.append(f"\n# total findings: {len(findings)}")
    return RawScanResult(
        engine=engine_name, targets=targets,
        raw_output="\n".join(raw_lines), findings=findings,
    )
