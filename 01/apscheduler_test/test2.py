# 进阶使用

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# 一个名为 default 的 MemoryJobStore
job_stores = {"default": MemoryJobStore()}
# 一个名为 default 的 ThreadPoolExecutor, 一个名为 processpool 的 ProcessPoolExecutor
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
# coalesce: 默认情况下，如果任务即将执行但之前的执行尚未完成，则最新的执行被视为误发。可以通过设置 `coalesce` 关键字参数为 `False` 来禁用此行为。
# max_instances: 默认情况下，同一时间只允许执行一个任务实例。这意味着，如果任务即将执行但之前的执行尚未完成，则最新的执行被视为误发。
#                可以通过在添加任务时使用 `max_instances` 关键字参数来设置调度器允许并发运行的特定任务的最大实例数。
# misfire_grace_time: 定义了一个任务可以延迟执行的最大时间范围（以秒为单位）。当任务未能在预定时间执行时，只要在这个grace time范围内，任务仍然会被执行。
job_defaults = {"coalesce": False, "max_instances": 2, "misfire_grace_time": 60}


# BackgroundScheduler：start() 立即返回，调度器在后台线程运行，适合嵌入 Web 服务、GUI 或还有其他主循环的程序
# 默认都会通过线程池并发执行任务
scheduler = BackgroundScheduler(
    job_stores=job_stores, executors=executors, job_defaults=job_defaults
)


def get_time_str():
    return f"{datetime.now(ZoneInfo('Asia/Shanghai')):%Y-%m-%d %H:%M:%S}"


def job1_func(*args, **kwargs):
    print(f"\033[0;36;40mJob 1 executed at {get_time_str()}\033[0m")


def job2_func(*args, **kwargs):
    print(f"\033[0;32;40mJob 2 executed at {get_time_str()}\033[0m")


def job3_func(arg1, arg2, *args, **kwargs):
    print(f"\033[0;33;40mJob 3 executed at {get_time_str()}, {arg1=}, {arg2=}\033[0m")


def job4_func(*args, **kwargs):
    print(f"\033[0;31;40mJob 4 executed at {get_time_str()}\033[0m")


def job5_func(*args, **kwargs):
    print(f"\033[0;35;40mJob 5 executed at {get_time_str()}\033[0m")


# 间隔2秒执行一次
job1 = scheduler.add_job(
    job1_func,
    "interval",
    seconds=2,
    max_instances=3,  # 最多同时运行3个实例
    misfire_grace_time=60,  # 容忍60秒的任务延迟
    id="job1",
)
# 间隔4秒执行一次
job2 = scheduler.add_job(job2_func, IntervalTrigger(seconds=4), id="job2")
# 5秒后执行
job3 = scheduler.add_job(
    job3_func,
    DateTrigger(run_date=datetime.now(ZoneInfo('Asia/Shanghai')) + timedelta(seconds=5)),
    args=["aaa"],
    kwargs={"arg2": "bbb"},
    id="job3",
)
# 当秒数为0或者5时, 执行
job4 = scheduler.add_job(job4_func, CronTrigger(second="*/5"), id="job4")
# 每个小时执行一次
job5 = scheduler.add_job(job5_func, CronTrigger(hour="*"), id="job5")


scheduler.start()


# 阻塞主线程, 直到按下Ctrl+C
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")