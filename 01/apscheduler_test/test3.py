# 使用一个任务唤醒另一个任务


import time
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# coalesce: 默认情况下，如果任务即将执行但之前的执行尚未完成，则最新的执行被视为误发。可以通过设置 `coalesce` 关键字参数为 `False` 来禁用此行为。
# max_instances: 默认情况下，同一时间只允许执行一个任务实例。这意味着，如果任务即将执行但之前的执行尚未完成，则最新的执行被视为误发。
#                可以通过在添加任务时使用 `max_instances` 关键字参数来设置调度器允许并发运行的特定任务的最大实例数。
job_defaults = {"coalesce": False, "max_instances": 2}
# 创建调度器
scheduler = BackgroundScheduler(job_defaults=job_defaults)


def some_condition():
    second = datetime.now(ZoneInfo("Asia/Shanghai")).second
    return second % 10 == 0


def job1_func(*args, **kwargs):
    print(f"\033[0;32;40mJob 1 executed at {time.strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    # 在某些条件下立即执行 job2
    # 如果 job2 使用 IntervalTrigger 作为 trigger, 这一次执行会刷新 job2 的下一次执行时间
    if some_condition():
        scheduler.modify_job(
            "job2", next_run_time=datetime.now(ZoneInfo("Asia/Shanghai"))
        )


def job2_func(*args, **kwargs):
    print(f"\033[0;35;40mJob 2 executed at {time.strftime('%Y-%m-%d %H:%M:%S')}\033[0m")


# 添加任务
job1 = scheduler.add_job(job1_func, IntervalTrigger(seconds=1), id="job1")
job2 = scheduler.add_job(job2_func, IntervalTrigger(seconds=8), id="job2")


# 启动调度器
scheduler.start()


# 阻塞主线程, 直到按下Ctrl+C
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")
