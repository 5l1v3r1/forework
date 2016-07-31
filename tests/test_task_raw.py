import json

import jupyter_client.session

from forework.tasks.raw import Raw


def test_init(test_image_1, test_conf):
    Raw(test_image_1, test_conf)


def test_run(test_image_1, test_conf):
    task = Raw(test_image_1, test_conf)
    task.start()
    assert task.done is True
    assert task.get_result().startswith('DOS/MBR boot sector;')
    assert task.get_warnings() == []
    next_tasks = task.to_dict()['next_tasks']
    assert len(next_tasks) == 1
    jdata = json.loads(next_tasks[0])
    assert jdata['name'] == ['Image']


def test_serialization(test_image_1, test_conf):
    task = Raw(test_image_1, test_conf)
    task.start()
    session = jupyter_client.session.Session()
    msg = session.msg(task.to_dict())
    session.serialize(msg)
