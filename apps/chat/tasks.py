from config import celery_app

@celery_app.task
def test_celery(arg):
    print('test_celery')
    print(arg)
