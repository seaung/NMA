"""漏洞去重辅助：指纹生成与重复识别"""
import hashlib

from app.models.vulnerabilities.vulnerability import Vulnerability


def build_fingerprint(name: str, cve_id: str = None, vuln_type: str = "") -> str:
    base = f"{cve_id or name}||{vuln_type or ''}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:32]


def find_duplicate(name: str, cve_id: str = None, vuln_type: str = "") -> Vulnerability | None:
    fp = build_fingerprint(name, cve_id, vuln_type)
    return Vulnerability.objects.filter(fingerprint=fp, is_deleted=False).first()
