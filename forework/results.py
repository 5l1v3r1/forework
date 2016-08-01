import json

import dateutil
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DEFAULT_RESULTS_FILE = 'results.json'
DEFAULT_PLOT_FILE = 'results.png'


class Results:
    '''
    Class that wraps the results obtained from a Forework Scheduler
    '''

    def __init__(self, results=None):
        self._results = results or []

    def __len__(self):
        return len(self._results)

    def __repr__(self):
        return '<{c}(results=<{n} tasks>)>'.format(
            c=self.__class__.__name__,
            n=len(self),
        )

    def __getitem__(self, item):
        '''
        Return all the tasks with the given name
        '''
        if type(item) == int:
            # address by index
            return self._results[item]
        else:
            # address by name
            res = []
            for task in self._results:
                if task._name == item:
                    res.append(task)
            return res

    def save(self, filename=DEFAULT_RESULTS_FILE):
        with open(filename, 'w') as fd:
            json.dump([x.to_dict() for x in self._results], fd)
        return filename

    def plot(self, filename=DEFAULT_PLOT_FILE, add_y_labels=False):
        min_date = None
        max_date = None
        yaxis = []
        labelsy = []
        for item in [x.to_dict() for x in self._results]:
            start = dateutil.parser.parse(item['start'])
            end = dateutil.parser.parse(item['end'])
            yaxis.append((start, end))
            if min_date is None or start < min_date:
                min_date = start
            if max_date is None or end > max_date:
                max_date = end
            if add_y_labels:
                path = item['path']
                if len(path) > 30:
                    path = path[:10] + '...' + path[-18:]
                labelsy.append(path)

        fig = plt.figure(figsize=(30, 60))
        ax = fig.add_subplot(111)

        for idx, (start, end) in enumerate(yaxis):
            start, end = mdates.date2num((start, end))
            ax.barh(idx + 0.2, end - start, height=0.8, left=start)

        # set Y labels (task names) properties
        plt.setp(
            plt.yticks(
                [i + 0.5 for i in range(len(yaxis))],
                labelsy,
                fontsize=14,
            )
        )

        # set X label (date/time) properties
        labelsx = ax.get_xticklabels()
        plt.setp(labelsx, rotation=30, fontsize=12)

        ax.xaxis_date()
        ax.invert_yaxis()
        fig.autofmt_xdate()
        plt.savefig(filename)
        plt.show()
        return filename
