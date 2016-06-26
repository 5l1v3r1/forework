import os
import json

from forework.tasks.raw import Raw


def test_init(images_dir):
    Raw(os.path.join(images_dir, '1-extend-part/ext-part-test-2.dd'))


def test_run(images_dir):
    task = Raw(os.path.join(images_dir, '1-extend-part/ext-part-test-2.dd'))
    task.run()
    assert task.done is True
    assert task.get_result().startswith('DOS/MBR boot sector;')
    next_tasks = task.to_dict()['next_tasks']
    assert len(next_tasks) == 1
    jdata = json.loads(next_tasks[0])
    assert jdata['name'] == 'MBR'
