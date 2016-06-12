import json

from . import (utils, config)

logger = utils.get_logger(__name__)

PRIO_LOW = -10
PRIO_NORMAL = 0
PRIO_HIGH = 10


def find_tasks(name=None):
    logger.info('Searching for tasks in %r', config.tasks_dir)
    import importlib
    modules = importlib.__import__('forework.tasks', fromlist='*')
    tasks = []
    for modulename in dir(modules):
        if modulename[:2] == '__':
            continue
        module = importlib.import_module(
            'forework.tasks.{m}'.format(m=modulename),
        )
        classes = [o for o in dir(module) if o[:2] != '__']
        for classname in classes:
            if classname == name or name is None:
                cls = getattr(module, classname)
                if type(cls) == type and cls != BaseTask and \
                        issubclass(cls, BaseTask):
                    tasks.append(cls)
    if name is not None:
        assert len(tasks) in (0, 1), ('Found more than one task named {t!r}'
                                      .format(t=name))
    return tasks


class BaseTask:

    mime_types = []

    def __init__(self, priority=PRIO_NORMAL, new_task_callback=None):
        self._name = self.__class__.__name__
        self._done = False
        self._priority = priority
        self.set_new_task_callback(new_task_callback)

    def __repr__(self):
        return '<{cls}(result={r!r})>'.format(
            cls=self.__class__.__name__,
            r=self._result if self._done else '<unfinished>',
        )

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
            'completed': self._done,
            'priority': self._priority,
            'result': self.get_result(),
        }

    @staticmethod
    def from_json(taskjson):
        '''
        Build a task from its JSON representation (see `to_json`)
        '''
        return json.loads(taskjson)

    @staticmethod
    def from_dict(taskdict):
        '''
        Build a task from its dict representation (see `to_dict`)
        '''
        cls = find_tasks(taskdict['name'])[0]
        task = cls(*taskdict['args'], priority=taskdict['priority'])
        task.done = taskdict['completed']
        task._result = taskdict['result']
        return task

    def set_new_task_callback(self, callback):
        self._on_new_task_callback = callback

    def call_new_task_callback(self, *args, **kwargs):
        if self._on_new_task_callback is None:
            logger.info('Got a new task but no user-defined method found')
            return None
        logger.debug('`on_new_task`(%r) called with args: %r | kwargs: %r',
                     self._on_new_task_callback,
                     args, kwargs)
        return self._on_new_task_callback(*args, **kwargs)

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
        self._done = value

    def start(self):
        self._done = False
        self.run()
        self._done = True
        return self

    def run(self):
        # NOTE: when overriding, remember to call self.done(True) to indicate
        #       that a task has completed and can yield a result
        msg = ('Attempted to call virtual method `run`, this method must be '
               'overridden')
        logger.warning(msg)
        raise NotImplementedError(msg)

    def get_result(self):
        if self.done():
            return self._result
        msg = 'Attempted to get results on a task that is still running'
        logger.warning(msg)
        return None
