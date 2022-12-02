from sqlalchemy import create_engine
from apscheduler.schedulers.blocking import BlockingScheduler

engine = create_engine('mysql+pymysql://dmp_user:jxm123.@47.105.107.235:3360/sospider')


def check_task():
    pass


sched = BlockingScheduler()
sched.add_job(check_task, trigger='interval', seconds=60, name="执行计划")
sched.start()
