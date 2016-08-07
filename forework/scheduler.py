import copy
import time
import asyncio
import datetime
import threading
import collections

import ipyparallel as parallel
import ipyparallel.error

from . import task_queue, utils, basetask, results
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
        self._config = None
        self._start_time = None
        self._end_time = None
        threading.Thread.__init__(self)

    def set_config(self, config):
        self._config = config

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
        self.enqueue(BaseTask.from_json(jsondata, self._config))

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
        tasks_to_retry_to_fetch = set()
        self._start_time = basetask.now()
        self._end_time = None
        while True:
            # stop if requested explicitly
            if not self._running:
                self._client.abort()
                break

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
            # sort tasks by task priority
            priority_tasks, remaining_tasks = [], []
            for task in new_tasks:
                if task.__class__.__name__ in self._config.priority:
                    priority_tasks.append(task)
                else:
                    remaining_tasks.append(task)
            prioritized_tasks = priority_tasks + remaining_tasks

            # add pending tasks to the pending task set used early in this loop
            amr = lview.map(lambda t: t.start(), prioritized_tasks)
            if amr:
                pending = pending.union(set(amr.msg_ids))

            # check if there are tasks to retry to fetch
            for msg_id in tasks_to_retry_to_fetch:
                try:
                    results = self._client.get_result(msg_id).get()
                except (ipyparallel.error.RemoteError, TypeError):
                    # will retry later
                    continue
                tasks_to_retry_to_fetch.remove(msg_id)
                # TODO this loop duplicates the code below. Remove duplication
                for result in results:
                    self._finished_tasks.append(result)
                    for jsontask in result.next_tasks:
                        self.enqueue_from_json(jsontask)
                    logger.info('Result: {r!r}'.format(r=result))

            # do something with the completed tasks
            for msg_id in finished:
                try:
                    results = self._client.get_result(msg_id).get()
                except (ipyparallel.error.RemoteError, TypeError):
                    tasks_to_retry_to_fetch.add(msg_id)
                    continue
                # NOTE keep this loop in sync with the loop above until the code
                # duplication is removed
                for result in results:
                    self._finished_tasks.append(result)
                    for jsontask in result.next_tasks:
                        self.enqueue_from_json(jsontask)
                    logger.info('Result: {r!r}'.format(r=result))

        self._end_time = basetask.now()

        if self._client is not None:
            self._client.wait()
            self.client = None
        self._running = False

    def stop(self):
        self._running = False
        if self._client is not None:
            self._client.wait()

        self.join()

    def wait(self):
        while True:
            if not self._running and self._end_time is not None:
                break
            time.sleep(.1)

    def is_running(self):
        return self._running is True

    @property
    def results(self):
        start_time = self._start_time
        end_time = self._end_time
        tasks = copy.copy(self._finished_tasks)
        if end_time is None:
            if start_time is not None:
                end_time = basetask.now()
        return results.Results(tasks, start_time, end_time)


def get():
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
