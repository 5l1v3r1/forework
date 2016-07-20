import json
import asyncio
import threading

import ipyparallel as parallel

from . import task_queue, utils, basetask
from .basetask import BaseTask

_scheduler = None

logger = utils.get_logger(__name__)


class Scheduler(threading.Thread):
    '''
    Task scheduler

    This class implements the task scheduler for submitting and executing new
    tasks
    '''

    def __init__(self):
        self._task_queue = task_queue.get()
        self._client = None
        self._running = False
        self._finished_tasks = []
        logger.debug('Initialized scheduler')
        threading.Thread.__init__(self)

    def enqueue(self, task):
        '''
        Add a new task to the queue and start processing it.

        A task must be a subclass of `forework.basetask.BaseTask`.
        '''
        logger.debug('Adding task: {t}'.format(t=task))
        self._task_queue.put_nowait(task)

    def enqueue_many(self, tasks):
        '''
        Add multiple tasks to the task queue, and start processing them.

        `tasks` is an iterable of BaseTask subclasses.
        '''
        logger.debug('Adding {n} tasks: {t}'.format(
            n=len(tasks),
            t=str(tasks)[:30],
        ))
        for task in tasks:
            self._task_queue.put_nowait(task)

    def enqueue_from_json(self, jsondata):
        '''
        Enqueue a task by creating it from a valid JSON description
        '''
        self.enqueue(BaseTask.from_json(jsondata))

    def _connect(self):
        '''
        Connect to the IPyParallel cluster
        '''
        logger.info('Connecting to the ipyparallel cluster')
        self._client = parallel.Client()

    def run(self):
        self._running = True
        logger.info('Starting task scheduler')

        # search for available task handlers
        self._tasks = basetask.find_tasks()

        # connect to the ipcluster instance
        self._connect()

        lview = self._client.load_balanced_view()
        pending = set()
        while self._running:
            # wait for completed tasks from the client
            try:
                self._client.wait(pending, 1e-1)
            except parallel.TimeoutError:
                pass

            # update finished and pending task sets
            finished = pending.difference(self._client.outstanding)
            pending = pending.difference(finished)

            # retrieve and start new tasks from the queue
            new_tasks = []
            while True:
                try:
                    new_tasks.append(self._task_queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            # add pending tasks to the pending task set used early in this loop
            amr = lview.map(lambda t: t.start(), new_tasks)
            if amr:
                pending = pending.union(set(amr.msg_ids))

            # do something with the completed tasks
            for msg_id in finished:
                for result in self._client.get_result(msg_id).get():
                    self._finished_tasks.append(result)
                    for jsontask in result.get_next_tasks():
                        self.enqueue_from_json(jsontask)
                    logger.info('Result: {r!r}'.format(r=result))
        if self._client is not None:
            self._client.wait()
            self.client = None

    def stop(self):
        self._running = False
        if self._client is not None:
            self._client.wait()
        self.join()

    def is_running(self):
        return self._running is True

    def save(self):
        '''
        Save the results to a JSON file
        '''
        if self._running:
            logger.error('The scheduler must be stopped before saving')
        with open('results.json', 'w') as fd:
            json.dump([x.to_dict() for x in self._finished_tasks], fd)
        logger.info('Saved finished tasks to results.json')


def get():
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
