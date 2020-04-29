import pytest

def test_test():
    hello_world = "Hello World"
    assert hello_world == "Hello World"

def test_always_passes():
    assert True

#This test will always fail
def test_always_fails():
    assert False
