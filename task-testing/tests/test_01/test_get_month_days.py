from simple_library_01.functions import get_month_days


def test_is_leap():
    assert 30 == get_month_days(1930, 1)
    assert 29 == get_month_days(2000, 2)
    assert 28 == get_month_days(2001, 2)
    try:
        get_month_days(2000, 13)
        assert False
    except AttributeError:
        pass
    assert 30 == get_month_days(2001, 6)
    assert 31 == get_month_days(2001, 5)