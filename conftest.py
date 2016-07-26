import os
import sys

import pytest

sys.path.insert(0, '..')
from forework.config import ForeworkConfig


@pytest.fixture
def images_dir():
    return os.path.join(os.path.dirname(__file__), 'tests/images')


@pytest.fixture
def test_image_1(images_dir):
    return os.path.join(images_dir, '1-extend-part/ext-part-test-2.dd')

@pytest.fixture
def test_conf():
    return ForeworkConfig('tests/test.yml')
