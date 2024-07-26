from typing import List
from celery import shared_task
from celery.signals import task_postrun


@shared_task
def scanner_from_nmap(target: str = '', ports: List[str] = []) -> None:
    return


@task_postrun.connect
def scanner_stop_to_collection():
    return


@shared_task
def scanner_from_masscan(target: str, rate: int, ports: List[str]) -> None:
    pass


@task_postrun.connect
def scanner_stop_to_collection_result():
    return

