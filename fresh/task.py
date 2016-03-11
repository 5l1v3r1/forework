class Task:

    def __init__(self, callable, args=None, kwargs=None):
        self._callable = callable
        self._args = args if args is not None else []
        self._kwargs = kwargs if kwargs is not None else {}
