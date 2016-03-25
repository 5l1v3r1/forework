from ..task import Task


class Fibonacci(Task):

    def __init__(self, n):
        self._n = n
        self._result = None
        self._done = False

    def run(self):
        n = self._n
        a, b = 0, 1
        for i in range(n):
            a, b = b, a + b
        self._result = a

    def get_result(self):
        return self._result

    def __repr__(self):
        return '<{c}(n={n!r}, result={r!r})>'.format(
            c=self.__class__.__name__,
            n=self._n,
            r=self._result if self._done else 'unfinished',
        )

