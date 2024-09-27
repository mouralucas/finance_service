import datetime

from services.utils.datetime import get_period_sequence, get_period


def test_get_period():
    date = datetime.date(2024, 6, 13)
    period = get_period(date)

    assert period == 202406

def test_get_previous_period():
    pass

def test_get_period_sequence():
    # Periods that change year
    start_period = 202310
    end_period = 202402

    range_period = get_period_sequence(start_period, end_period)
    assert len(range_period) == 5
    assert 202313 not in range_period

    # Periods within the same year
    start_period = 202301
    end_period = 202312

    range_period = get_period_sequence(start_period, end_period)
    assert len(range_period) == 12

    # Periods that change year more than once
    start_period = 202104
    end_period = 202406

    range_period = get_period_sequence(start_period, end_period)
    assert len(range_period) == 39
    assert 202113 not in range_period
    assert 202213 not in range_period
    assert 202313 not in range_period