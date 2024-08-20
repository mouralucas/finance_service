import datetime

from services.credit_card import CreditCardService


def test_set_due_date():
    # Test transaction before the closing day in the same month
    transaction_date = datetime.date(year=2024, month=8, day=7)
    close_day = 13
    due_day = 20
    expected_due_date = '2024-08-20'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction ON the closing day in the same month
    transaction_date = datetime.date(year=2024, month=8, day=13)
    close_day = 13
    due_day = 20
    expected_due_date = '2024-09-20'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction after the closing day in the same month
    transaction_date = datetime.date(year=2024, month=8, day=25)
    close_day = 13
    due_day = 20
    expected_due_date = '2024-09-20'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction before closing with closing in the month before the due date
    transaction_date = datetime.date(year=2024, month=8, day=25)
    close_day = 28
    due_day = 5
    expected_due_date = '2024-09-05'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction ON teh closing day with closing in the month before the due date
    transaction_date = datetime.date(year=2024, month=8, day=28)
    close_day = 28
    due_day = 5
    expected_due_date = '2024-10-05'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction in same month as due and closing in the month before the due date
    transaction_date = datetime.date(year=2024, month=9, day=5)
    close_day = 28
    due_day = 5
    expected_due_date = '2024-10-05'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date

    # Test transaction before the closing day with closing in the month before the due date
    transaction_date = datetime.date(year=2024, month=8, day=27)
    close_day = 28
    due_day = 5
    expected_due_date = '2024-09-05'

    due_date = CreditCardService.set_due_date(transaction_date, close_day, due_day, return_str=True)
    assert due_date == expected_due_date
