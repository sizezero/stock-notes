from date import *
from nose.tools import *
import context
from stocks import entries

def setup():
    print("SETUP!")

def teardown():
    print("TEAR DOWN!")

# verify we can at least load the stock entries
def test_load():
    assert len(entries) > 0

