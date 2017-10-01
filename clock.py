from datetime import datetime, timedelta
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from pq import PQ
from psycopg2 import connect

from app import db, Task

# Set up connection to queue.
DB_URL_DEFAULT = 'postgresql://postgres@localhost/judicious'
DB_URL = os.environ.get("DATABASE_URL", DB_URL_DEFAULT)
conn = connect(DB_URL)
pq = PQ(conn)
todo_queue = pq['tasks']

# Set up logging.
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s [clock.1]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Set up scheduler.
sched = BlockingScheduler()

JUDICIOUS_RECRUIT_INTERVAL = os.environ.get(
    "JUDICIOUS_RECRUIT_INTERVAL", 150000)

JUDICIOUS_CLEANUP_INTERVAL = os.environ.get(
    "JUDICIOUS_CLEANUP_INTERVAL", 5)


@sched.scheduled_job('interval', seconds=JUDICIOUS_RECRUIT_INTERVAL)
def recruitment():
    logger.info('Recruitment.')


@sched.scheduled_job('interval', seconds=JUDICIOUS_CLEANUP_INTERVAL)
def cleanup():
    logger.info('Cleanup.')
    incomplete_tasks = Task.query\
        .filter_by(in_progress=True).filter_by(result=None).all()
    for task in incomplete_tasks:
        duration = datetime.now() - task.started_at
        logger.info(duration)
        if duration > timedelta(seconds=30):
            logger.info("Timeout on task {}".format(task.id))
            task.in_progress = False
            task.started_at = None
            db.session.add(task)
            db.session.commit()
            todo_queue.put({"id": task.id})


sched.start()