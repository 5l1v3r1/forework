PRIO_LOW = -10
PRIO_NORMAL = 0
PRIO_HIGH = 10


class TaskRunningException(Exception):
    pass


class Task:

    def __init__(self, priority=PRIO_NORMAL):
        self._done = False
        self._priority = priority

    def __repr__(self):
        return '<{cls}(result={r!r})>'.format(
            cls=self.__class__.__name__,
            r=self._result if self._done else '<unfinished>',
        )

    def done(self, value=None):
        if value not in (True, False, None):
            raise Exception(
                'Value for {cls}.done() must be either True, False or None'
                .format(cls=self.__class__.__name__),
            )
        if value in (True, False):
            self._done = value
        else:
            return self._done

    def start(self):
        self._done = False
        self.run()
        self._done = True
        return self

    def run(self):
        # NOTE: when overriding, remember to call self.done(True) to indicate
        #       that a task has completed and can yield a result
        raise NotImplementedError('The `run` method must be overridden')

    def get_result(self):
        if self.done():
            return self._result
        raise TaskRunningException
