import json

from forework.tasks.mbr import MBR


def test_init(test_image_1):
    MBR(test_image_1)


def test_run(test_image_1):
    task = MBR(test_image_1)
    task.start()
    assert task.done is True
    assert task.get_warnings() == []
    results = task.get_result()
    assert results[0] == 'DOS 3.0+ 16-bit FAT (up to 32M)'
    assert results[1] == 'DOS 3.0+ 16-bit FAT (up to 32M)'
    assert results[2] == 'DOS 3.0+ 16-bit FAT (up to 32M)'
    assert results[3] == 'DOS 3.3+ Extended Partition'

    assert len(task.get_next_tasks()) == 3
    for next_task in task.get_next_tasks():
        jdata = json.loads(next_task)
        assert jdata['name'] == 'DOSPartition'
