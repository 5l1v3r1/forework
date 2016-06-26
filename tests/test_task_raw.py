import json

from forework.tasks.raw import Raw


def test_init(test_image_1):
    Raw(test_image_1)


def test_run(test_image_1):
    task = Raw(test_image_1)
    task.run()
    assert task.done is True
    assert task.get_result().startswith('DOS/MBR boot sector;')
    assert task.get_warnings() == []
    next_tasks = task.to_dict()['next_tasks']
    assert len(next_tasks) == 1
    jdata = json.loads(next_tasks[0])
    assert jdata['name'] == 'MBR'
