"""Celery 任务：执行扫描任务、落库 ScanResult、去重创建漏洞与关联资产"""
from __future__ import annotations

from django.utils import timezone

from app.configs.celery import app
from app.services.scan_engines.factory import get_engine


def _collect_targets(task) -> list[str]:
    targets: list[str] = list(task.targets or [])
    for a in task.assets.all():
        if a.ip:
            targets.append(a.ip)
        elif a.web_url:
            targets.append(a.web_url)
        elif a.domain:
            targets.append(a.domain)
    # 去重保序
    seen = set()
    ordered = []
    for t in targets:
        if t and t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered


def execute_scan(task_id: int) -> dict:
    """同步执行扫描（被 Celery 任务包裹，也可被 API 同步调用）。"""
    from app.models.assets.assets import Asset
    from app.models.tasks.task import ScanResult, Task, TaskLog
    from app.models.vulnerabilities.vulnerability import Vulnerability, VulnerabilityAsset

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return {"error": "task not found"}

    now = timezone.now()
    task.status = "running"
    task.actual_start_time = now
    task.progress = 5
    task.error_message = ""
    task.save(update_fields=["status", "actual_start_time", "progress", "error_message"])

    log = TaskLog.objects.create(task=task, status="running", start_time=now)
    try:
        targets = _collect_targets(task)
        if not targets:
            raise ValueError("没有可用的扫描目标，请在任务中填写目标或关联资产。")

        engine = get_engine(task.engine, task.scan_config or {})
        config = dict(task.scan_config or {})
        config.setdefault("ports", task.scan_ports or "1-1000")

        result = engine.run(targets, config)

        ScanResult.objects.create(
            task=task,
            raw_output=result.raw_output,
            parsed=[vars(f) for f in result.findings],
        )
        task.progress = 60
        task.save(update_fields=["progress"])

        created_count = 0
        for f in result.findings:
            asset = None
            if f.target:
                asset = Asset.objects.filter(ip=f.target).first()
                if not asset and f.target.startswith("http"):
                    asset = Asset.objects.filter(web_url__icontains=f.target).first()
            fp = f"{task.engine}::{f.name}::{f.port}::{f.target}"
            vuln, was_created = Vulnerability.objects.get_or_create(
                fingerprint=fp,
                defaults=dict(
                    name=f.name,
                    description=f.description or "",
                    cve_id=f.cve_id,
                    risk_level=f.risk_level,
                    cvss_score=f.cvss_score,
                    vuln_type=f.vuln_type,
                    solution=f.solution or "",
                    source="scan",
                    status="unverified",
                    created_by=task.creator,
                ),
            )
            if was_created:
                created_count += 1
            if asset:
                VulnerabilityAsset.objects.get_or_create(
                    vulnerability=vuln,
                    asset=asset,
                    defaults=dict(
                        port=f.port,
                        protocol=f.protocol,
                        component=f.component,
                        version=f.version,
                        evidence=f"扫描引擎 {result.engine} 发现",
                    ),
                )
                ports = list(asset.ports or [])
                if f.port and f.port not in [str(p) for p in ports]:
                    ports.append(int(f.port) if str(f.port).isdigit() else f.port)
                    asset.ports = ports
                    asset.last_scan_time = now
                    asset.save(update_fields=["ports", "last_scan_time"])

        finished = timezone.now()
        task.status = "success"
        task.progress = 100
        task.completed_time = finished
        task.result_summary = (
            f"扫描完成：目标 {len(targets)} 个，发现风险 {len(result.findings)} 项，"
            f"新增漏洞 {created_count} 个。"
        )
        task.save(update_fields=["status", "progress", "completed_time", "result_summary"])

        log.status = "success"
        log.end_time = finished
        log.duration = int((finished - log.start_time).total_seconds())
        log.result = task.result_summary
        log.save(update_fields=["status", "end_time", "duration", "result"])
        return {"created": created_count, "findings": len(result.findings)}
    except Exception as exc:  # noqa: BLE001
        finished = timezone.now()
        task.status = "failed"
        task.error_message = str(exc)[:2000]
        task.completed_time = finished
        task.save(update_fields=["status", "error_message", "completed_time"])
        log.status = "failed"
        log.end_time = finished
        log.duration = int((finished - log.start_time).total_seconds())
        log.error_message = str(exc)[:2000]
        log.save(update_fields=["status", "end_time", "duration", "error_message"])
        raise


@app.task(bind=True, max_retries=3)
def run_scan_task(self, task_id: int):
    try:
        return execute_scan(task_id)
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc, countdown=10)
