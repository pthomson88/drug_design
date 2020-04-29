#We're in the test directory so we need to jump back to the root dir to find modules
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import pytest

from main import create_app

@pytest.fixture
def app():
    app = create_app()
    return app
