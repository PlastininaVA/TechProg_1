from simple_library_01.functions import is_leap


def test_is_leap():
    assert False == is_leap(2001)
    assert True == is_leap(2004)
    assert True == is_leap(2000)
    assert False == is_leap(2100)
    try:
        is_leap(-20)
        assert False
    except AttributeError:
        pass
