import re
import json
import datetime

from . import (utils, config)

logger = utils.get_logger(__name__)

PRIO_LOW = -10
PRIO_NORMAL = 0
PRIO_HIGH = 10

_tasks_cache = {}


def _rebuild_cache():
    global _tasks_cache
    logger.info('Rebuilding tasks cache from %r', config.tasks_dir)
    import importlib
    modules = importlib.__import__('forework.tasks', fromlist='*')
    tasks = {}
    for modulename in dir(modules):
        if modulename[:2] == '__':
            continue
        module = importlib.import_module(
            'forework.tasks.{m}'.format(m=modulename),
        )
        classes = [o for o in dir(module) if o[:2] != '__']
        for classname in classes:
            # We don't want Raw in the task cache to avoid loops
            if classname == 'Raw':
                continue
            cls = getattr(module, classname)
            if type(cls) == type and cls != BaseTask and \
                    issubclass(cls, BaseTask):
                tasks[classname] = cls
    _tasks_cache = tasks
    logger.debug('Tasks cache rebuilt: {n} tasks found'.format(n=len(tasks)))


def find_tasks(name=None, rebuild_cache=False):
    '''
    Discover all the available tasks. If `name` is not None, it will search only
    tasks matching that name. If `rebuild_cache` is True, it will invalidate and
    rebuild the tasks cache even if task caching is enabled.
    If task caching is not enabled (see forework.config.ENABLE_TASKS_CACHE), the
    task list will be rebuilt at every call, which is very inefficient
    '''
    global _tasks_cache
    if config.ENABLE_TASKS_CACHE and not rebuild_cache:
        if _tasks_cache is None:
            logger.info('Tasks cache enabled but cache is empty. Performing '
                        'task search')
        else:
            _rebuild_cache()

    if name is not None:
        tasks_found = [_tasks_cache[name]]
    else:
        tasks_found = list(_tasks_cache.values())
    logger.info('Tasks found: {t}'.format(t=tasks_found))
    return tasks_found


def find_tasks_by_filetype(filetype, first_only=True):
    '''
    Search for tasks that can handle a file type (described as a string), and
    return their names as a list of strings. If `first_only` is True, only the
    first task name is returned, as a string.
    '''
    logger.info('Searching for tasks that can handle %r', filetype)
    all_tasks = find_tasks()
    suitable_tasks = []
    for task in all_tasks:
        if task.can_handle(filetype):
            if first_only:
                return [task.__name__]
            suitable_tasks.append(task.__name__)
    return suitable_tasks


class BaseTask:

    MAGIC_PATTERN = None
    _rx = None

    def __init__(self, path, offset=0, priority=PRIO_NORMAL,
                 time_function=None):
        self._name = self.__class__.__name__
        self._path = path
        self._offset = offset
        self._done = False
        self._start = None
        self._end = None
        if time_function is None:
            self._time_function = self.now
        else:
            self._time_function = time_function
        self._result = None
        self._warnings = []
        self._priority = priority
        self._next_tasks = []

    def __repr__(self):
        return '<{cls}(result={r!r})>'.format(
            cls=self.__class__.__name__,
            r=self._result if self._done else '<unfinished>',
        )

    def now(self):
        return str(datetime.datetime.now())

    @classmethod
    def can_handle(self, magic_string):
        if self.MAGIC_PATTERN is None:
            raise Exception('MAGIC_PATTERN must be defined by the task {name}'
                            .format(name=self._name))
        if self._rx is None:
            self._rx = re.compile(self.MAGIC_PATTERN)
        return self._rx.match(magic_string)

    def to_json(self):
        '''
        Return a JSON representation of this task and its status.

        This method wraps around to_dict and should not be overridden.
        '''
        return json.dumps(self.to_dict())

    def to_dict(self):
        '''
        Return a dict representation of this task and its status.

        This method returns basic task information and should be overridden by
        derived tasks.
        Derived tasks can reuse the dict returned by this method and add or
        amend part of the information. They should never remove items though.
        All the items must be JSON-serializable.
        '''
        return {
            'name': self._name,
            'path': self._path,
            'offset': self._offset,
            'completed': self._done,
            'start': self._start,
            'end': self._end,
            'priority': self._priority,
            'result': self.get_result(),
            'next_tasks': self.get_next_tasks(),
            'warnings': self.get_warnings(),
        }

    @staticmethod
    def from_json(taskjson):
        '''
        Build a task from its JSON representation (see `to_json`)
        '''
        return BaseTask.from_dict(json.loads(taskjson))

    @staticmethod
    def from_dict(taskdict):
        '''
        Build a task from its dict representation (see `to_dict`)
        '''
        task_name = taskdict['name'][0]
        cls = find_tasks(task_name)[0]
        path = taskdict['path']
        path = taskdict.get('offset', 0)
        args = taskdict.get('args', [])
        task = cls(path, *args, priority=taskdict.get('priority', PRIO_NORMAL))
        task.done = taskdict.get('completed', False)
        task._result = taskdict.get('result', None)
        return task

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, value):
        if type(value) != bool:
            raise Exception(
                'Value for {cls}.done must be a boolean'
                .format(cls=self.__class__.__name__),
            )
        if value is False:
            self._start = self._time_function()
        else:
            self._end = self._time_function()
        self._done = value

    def add_next_task(self, jsondata):
        '''
        Add a new follow-up task to the next_tasks list. The input is a valid
        JSON representation of a task.
        '''
        self._next_tasks.append(jsondata)

    def get_next_tasks(self):
        '''
        Return the list of tasks to do next. Every task is in JSON format.
        '''
        return [json.dumps(t) for t in self._next_tasks]

    def add_warning(self, message):
        '''
        Add a warning message to the task's warnings
        '''
        logger.warn(message)
        self._warnings.append(message)

    def get_warnings(self):
        '''
        Return the list of warnings generated by the task
        '''
        return self._warnings

    def start(self):
        self.done = False
        logger.info('Task {tn} started at {ts}'.format(
            tn=self.__class__.__name__,
            ts=self._start,
        ))
        self.run()
        self.done = True
        logger.info('Task {tn} ended at {ts}'.format(
            tn=self.__class__.__name__,
            ts=self._end,
        ))
        return self

    def run(self):
        # NOTE: when overriding, remember to call self.done(True) to indicate
        #       that a task has completed and can yield a result
        msg = ('Attempted to call virtual method `run` on {myself}, this '
               'method must be overridden'.format(
                   myself=self.__class__.__name__)
               )
        logger.warning(msg)
        raise NotImplementedError(msg)

    def get_result(self):
        if self.done:
            return self._result
        msg = 'Attempted to get results on a task that is still running'
        logger.warning(msg)
        return None
