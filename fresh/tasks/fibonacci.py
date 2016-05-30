from ..task import Task


class Fibonacci(Task):

    def __init__(self, n, *args, **kwargs):
        self._n = n
        Task.__init__(self, *args, **kwargs)

    def run(self):
        n = self._n
        a, b = 0, 1
        for i in range(n):
            a, b = b, a + b
        self._result = a
        self.done = True

    def __repr__(self):
        return '<{cls}(n={n!r}, result={r!r})>'.format(
            cls=self.__class__.__name__,
            n=self._n,
            r=self._result if self.done else '<unfinished>',
        )
