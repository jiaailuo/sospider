import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from apscheduler.schedulers.blocking import BlockingScheduler
from dto.dotask import DoTaskDTO
from executor.kettle import KettleExecutor
import time


# engine = create_engine('mysql+pymysql://sq_dev:soquant.123@10.80.1.95:3306/sospider')
engine = create_engine('mysql+pymysql://dmp_user:jxm123.@47.105.107.235:3360/sofeeder')
engine = create_engine('mysql+pymysql://localhost:3360/sofeeder')


def do_task():
    # 获取一个任务对象
    task = dequeue()
    if task is not None:
        print("执行采集任务:{0}.{1},任务id:{2}".format(task.space, task.name, task.id))
        if task.executor == "kettle":
            executor = KettleExecutor(task.kettle, task.bdate)
            executor.ExecJob()
            time.sleep(10)
            print(executor.Status)


def dequeue():
    # 读待执行的第一条任务
    sql = "select id,bdate,options,space,`name`,`do` from v_queue_waiting_do order by plan_time asc limit 0,1"
    data = pd.read_sql(sql, engine)
    if data.empty:
        return None
    else:
        # 设置任务状态：执行中
        update_sql = "update sys_etl_dos set `status` = 1 where id={0}".format(data.loc[0]["id"])
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(update_sql))
        # 构建任务对象
        task = DoTaskDTO(dict(data.loc[0]))
        return task


if __name__ == '__main__':
    sched = BlockingScheduler()
    # sched.add_job(do_task, trigger='interval', seconds=60, name="执行计划")
    sched.add_job(do_task, trigger='date', next_run_time=datetime.datetime.now())
    sched.start()


