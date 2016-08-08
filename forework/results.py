import json
import datetime
import itertools
import subprocess
import collections

import dateutil
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DEFAULT_RESULTS_FILE = 'results.json'
DEFAULT_PLOT_FILE = 'results.png'
DEFAULT_DENSITY_PLOT_FILE = 'results_density.png'
DEFAULT_EDITOR = 'vim'

# List of tasks to skip size computation for
CONTAINERS = ['Image', 'DirectoryScanner']


def bytes_to_human_readable_size(size):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size / 1024. >= 1:
            size /= 1024.
        else:
            break
    return '{s:.3f} {u}'.format(s=size, u=unit)


def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk


class Results:
    '''
    Class that wraps the results obtained from a Forework Scheduler
    '''

    def __init__(self, results=None, start=None, end=None):
        self._results = results or []
        self._size = None
        if start is None:
            start = None
        elif not isinstance(start, datetime.datetime):
            start = dateutil.parser.parse(start)
        self.start = start

        if end is None:
            end = None
        elif not isinstance(end, datetime.datetime):
            end = dateutil.parser.parse(end)
        self.end = end

    def __len__(self):
        return len(self._results)

    def __repr__(self):
        return '<{c}(results=<{n} tasks>)>'.format(
            c=self.__class__.__name__,
            n=len(self),
        )

    def size(self):
        if self._size is None:
            size = 0
            for task in self._results:
                if task.__class__.__name__ not in CONTAINERS:
                    size += task._size
            self._size = size
        return self._size

    def __getitem__(self, item):
        '''
        Return all the tasks with the given name
        '''
        if type(item) == int:
            # address by index
            return self._results[item]
        elif type(item) == slice:
            return Results(self._results[item], self.start, self.end)
        else:
            # address by name
            res = []
            for task in self._results:
                if task._name == item:
                    res.append(task)
            return Results(res, self.start, self.end)

    def save(self, filename=DEFAULT_RESULTS_FILE):
        with open(filename, 'w') as fd:
            json.dump([x.to_dict() for x in self._results], fd)
        return filename

    def plot(self, filename=DEFAULT_PLOT_FILE, add_y_labels=True,
             colours=True, exclude=None):
        min_date = None
        max_date = None
        yaxis = []
        labelsy = []
        colour_by_task = {}
        col_idx = 0
        for item in self._results:
            if exclude and item._name in exclude:
                continue
            start = item.start_time
            end = item.end_time
            if colours:
                if item._name not in colour_by_task:
                    # TODO handle IndexError
                    colour = list(matplotlib.colors.cnames.keys())[col_idx]
                    colour_by_task[item._name] = colour
                    col_idx += 1
                else:
                    colour = colour_by_task[item._name]
            else:
                colour = 'aliceblue'
            yaxis.append((start, end, colour))
            if min_date is None or start < min_date:
                min_date = start
            if max_date is None or end > max_date:
                max_date = end
            if add_y_labels:
                labelsy.append(item._name)

        fig = plt.figure(figsize=(30, 60))
        ax = fig.add_subplot(111)

        for idx, (start, end, colour) in enumerate(yaxis):
            start, end = mdates.date2num((start, end))
            ax.barh(idx + 0.2, end - start, height=0.8, left=start,
                    color=matplotlib.colors.cnames[colour])

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

    def density(self, what, every=None, percent=None,
                filename=DEFAULT_DENSITY_PLOT_FILE):
        if every is not None and percent is not None:
            raise Exception('You must use either `every` or `percent`')
        if every is None:
            if percent is None:
                percent = 10  # default percentage
            chunklen = round(len(self._results) / 100 * float(percent))
        else:
            chunklen = every

        samples = []
        for chunk in grouper(chunklen, self._results):
            samples.append(len([None for t in chunk if t._name == what]))

        # generate bar chart
        width = 1
        fig, ax = plt.subplots()
        ax.set_ylabel('Frequency of {w}'.format(w=what))
        ax.set_title('Distribution of the frequency of {w}'.format(w=what))
        ax.set_xticks(range(0, len(samples), width))
        ax.set_xticklabels(['t{n}'.format(n=n) for n in range(len(samples))])

        ax.bar(range(0, len(samples), width), samples, width * 0.8)
        plt.savefig(filename)
        plt.show()
        return samples

    def edit(self, item_or_path_or_index, editor=DEFAULT_EDITOR):
        if type(item_or_path_or_index) == int:
            item = self[item_or_path_or_index].path
        elif type(item_or_path_or_index) == str:
            item = item_or_path_or_index
        else:
            item = item_or_path_or_index.path
        subprocess.call([editor, item])

    def stats(self):
        if self.start is None or self.end is None:
            duration = '<unknown>'
        else:
            duration = self.end - self.start
        counter = collections.Counter([t._name for t in self._results])
        top10 = ''
        for (task, frequency) in counter.most_common(10):
            top10 += '        {t} (appeared {f} times)\n'.format(
                t=task,
                f=frequency,
            )
        hrsize = bytes_to_human_readable_size(self.size())
        print(
            'Start time       : {start}\n'
            'End time         : {end}\n'
            'Duration         : {duration}\n'
            'Analyzed objects : {nobj}\n'
            'Total size       : {size} bytes ({hrsize})\n'
            'Top file types   : \n{top10}\n'.format(
                start=self.start,
                end=self.end,
                duration=duration,
                nobj=len(self._results),
                size=self.size(),
                hrsize=hrsize,
                top10=top10,
            )
        )

    def in_range(self, start_time, end_time, assume_sorted=True):
        '''
        Return all the tasks that are entirely in a given time range.

        Assume that the tasks are sorted (they should be), unless assume_sorted
        is False
        '''
        if not isinstance(start_time, datetime.datetime):
            start_time = dateutil.parser.parse(start_time)
        if not isinstance(end_time, datetime.datetime):
            end_time = dateutil.parser.parse(end_time)
        ret = []
        for item in self._results:
            if item.start_time >= start_time and item.end_time <= end_time:
                ret.append(item)
            if assume_sorted and item.start_time > end_time:
                break
        return Results(ret, self.start, self.end)
