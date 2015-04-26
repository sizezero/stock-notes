from date import *
from nose.tools import *
import context
from date import *

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_parse():
    assert parseDate("apr 24, 1968") == Date(1968,4,24)
    assert parseDate("APR 24, 1968") == Date(1968,4,24)
    assert parseDate("foo 24, 1968") == None

