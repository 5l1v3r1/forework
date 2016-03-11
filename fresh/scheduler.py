import multiprocessing

from . import task_queue

_scheduler = None

class Scheduler:

    def __init__(self, max_parallel_tasks=multiprocessing.cpu_count()):
        self.task_queue = task_queue.get()
        self.max_parallel_tasks = max_parallel_tasks

    def enqueue(self, task):
        pass

    def run(self):
        pass


def get():
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
