from celery import shared_task


@shared_task
def send_message():
    return {"msg": "ok"}

