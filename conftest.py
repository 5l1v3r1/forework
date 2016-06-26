import os
import sys

import pytest

sys.path.insert(0, '..')


@pytest.fixture
def images_dir():
    return os.path.join(os.getcwd(), 'tests/images')
