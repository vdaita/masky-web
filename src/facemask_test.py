from . import facemask

def test_facemask():
    assert facemask.apply("Jane") == "hello Jane"
