from __future__ import absolute_import
from celery import Celery

from aleph import SampleManager

tasker = Celery('aleph',
            broker='amqp://',
            backend='amqp://',
            include=['aleph.tasks'])

tasker.conf.update({
    'CELERYBEAT_SCHEDULE': {
        'samplemanager-consume-sample': {
            'task': 'tasks.sample_consume',
            'schedule': timedelta(seconds=30),
        },
    },
    'CELERY_TIMEZONE': 'UTC',
    'CELERY_TASK_RESULT_EXPIRES': 3600,
    })

# Tasks

@tasker.task
def sample_consume():

    sm = SampleManager()
    print sm


if __name__ == '__main__':
    tasker.start()
