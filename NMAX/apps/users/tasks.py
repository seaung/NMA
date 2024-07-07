from celery import shared_task


@shared_task
def send_email(msg: str, body: str) -> None:
    return None

