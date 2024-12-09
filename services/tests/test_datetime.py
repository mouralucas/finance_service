from datetime import date

from services.utils.datetime import get_period_range, get_period, get_previous_period, get_installments_due_dates


def test_get_period():
    reference_date = date(2024, 6, 13)
    period = get_period(reference_date)

    assert period == 202406


def test_get_previous_period():
    pass


def test_get_period_sequence():
    # Periods that change year
    start_period = 202310
    end_period = 202402

    range_period = get_period_range(start_period, end_period)
    assert len(range_period) == 5
    assert 202313 not in range_period

    # Periods within the same year
    start_period = 202301
    end_period = 202312

    range_period = get_period_range(start_period, end_period)
    assert len(range_period) == 12

    # Periods that change year more than once
    start_period = 202104
    end_period = 202406

    range_period = get_period_range(start_period, end_period)
    assert len(range_period) == 39
    assert 202113 not in range_period
    assert 202213 not in range_period
    assert 202313 not in range_period


def test_get_periods_back():
    period = get_previous_period(period=202410, offset=5)
    assert period == 202405

    # Assert offset that change one year
    period = get_previous_period(period=202410, offset=12)
    assert period == 202310


def test_get_installments_due_date():
    # Test day before close, but in the same year
    transaction_date = date(2024, 12, 1)
    close_day = 13
    due_day = 20
    tot_installments = 2

    # Expecting dates:
    # 2024-12-20
    # 2025-01-20
    installments_due_dates = get_installments_due_dates(transaction_date=transaction_date, due_day=due_day, close_day=close_day, tot_installments=tot_installments)
    assert type(installments_due_dates) is list
    assert len(installments_due_dates) == tot_installments
    assert date(2024, 12, 20) == installments_due_dates[0]['due_date']
    assert date(2025, 1, 20) == installments_due_dates[1]['due_date']

    # Test day after close, but in the same month
    transaction_date = date(2024, 12, 14)
    close_day = 13
    due_day = 20
    tot_installments = 5

    # Expecting dates:
    # 2025-01-20
    # 2025-02-20
    # 2025-03-20
    # 2025-04-20
    # 2025-05-20
    installments_due_dates = get_installments_due_dates(transaction_date=transaction_date, due_day=due_day, close_day=close_day, tot_installments=tot_installments)
    assert type(installments_due_dates) is list
    assert len(installments_due_dates) == tot_installments
    assert date(2025, 1, 20) == installments_due_dates[0]['due_date']
    assert date(2025, 2, 20) == installments_due_dates[1]['due_date']
    assert date(2025, 3, 20) == installments_due_dates[2]['due_date']
    assert date(2025, 4, 20) == installments_due_dates[3]['due_date']
    assert date(2025, 5, 20) == installments_due_dates[4]['due_date']

    # Test day before close, but in the month before
    transaction_date = date(2024, 11, 25)
    close_day = 13
    due_day = 20
    tot_installments = 3

    # Expecting dates:
    # 2025-01-20
    # 2025-02-20
    # 2025-03-20
    # 2025-04-20
    # 2025-05-20
    installments_due_dates = get_installments_due_dates(transaction_date=transaction_date, due_day=due_day, close_day=close_day, tot_installments=tot_installments)
    assert type(installments_due_dates) is list
    assert len(installments_due_dates) == tot_installments
    assert date(2024, 12, 20) == installments_due_dates[0]['due_date']
    assert date(2025, 1, 20) == installments_due_dates[1]['due_date']
    assert date(2025, 2, 20) == installments_due_dates[2]['due_date']

    # Test at close day
    transaction_date = date(2024, 12, 13)
    close_day = 13
    due_day = 20
    tot_installments = 4

    # Expecting dates:
    # 2025-01-20
    # 2025-02-20
    # 2025-03-20
    # 2025-04-20
    # 2025-05-20
    installments_due_dates = get_installments_due_dates(transaction_date=transaction_date, due_day=due_day, close_day=close_day, tot_installments=tot_installments)
    assert type(installments_due_dates) is list
    assert len(installments_due_dates) == tot_installments
    assert date(2025, 1, 20) == installments_due_dates[0]['due_date']
    assert date(2025, 2, 20) == installments_due_dates[1]['due_date']
    assert date(2025, 3, 20) == installments_due_dates[2]['due_date']
    assert date(2025, 4, 20) == installments_due_dates[3]['due_date']

    # Test at day after close
    transaction_date = date(2024, 12, 12)
    close_day = 13
    due_day = 20
    tot_installments = 2

    # Expecting dates:
    # 2025-01-20
    # 2025-02-20
    # 2025-03-20
    # 2025-04-20
    # 2025-05-20
    installments_due_dates = get_installments_due_dates(transaction_date=transaction_date, due_day=due_day, close_day=close_day, tot_installments=tot_installments)
    assert type(installments_due_dates) is list
    assert len(installments_due_dates) == tot_installments
    assert date(2024, 12, 20) == installments_due_dates[0]['due_date']
    assert date(2025, 1, 20) == installments_due_dates[1]['due_date']


