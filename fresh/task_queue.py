import asyncio

_task_queue = None

def init(maxsize=0):
    global _task_queue
    _task_queue = asyncio.Queue(maxsize)


def get():
    global _task_queue
    if _task_queue is None:
        init()
    return _task_queue
