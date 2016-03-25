class Task:

    def __init__(self):
        self._done = False

    def done(self):
        return self._done

    def start(self):
        self._done = False
        self.run()
        self._done = True
        return self

    def run(self):
        raise NotImplementedError('The `run` method must be overridden')

    def get_result(self):
        raise NotImplementedError('The `get_result` method must be overridden')
