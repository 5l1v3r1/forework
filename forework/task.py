from . import utils

logger = utils.get_logger(__name__)

PRIO_LOW = -10
PRIO_NORMAL = 0
PRIO_HIGH = 10


class TaskRunningException(Exception):
    pass


class Task:

    mime_types = []

    def __init__(self, priority=PRIO_NORMAL, new_task_callback=None):
        self._done = False
        self._priority = priority
        self.set_new_task_callback(new_task_callback)

    def __repr__(self):
        return '<{cls}(result={r!r})>'.format(
            cls=self.__class__.__name__,
            r=self._result if self._done else '<unfinished>',
        )

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
        raise TaskRunningException(msg)
