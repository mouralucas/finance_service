import calendar
import datetime
import random


def get_current_period():
    today = datetime.datetime.now(datetime.timezone.utc)
    month = today.month
    year = today.year

    return year * 100 + month


def get_period(date: datetime.date | datetime.datetime) -> int:
    year = date.year
    month = date.month
    return year * 100 + month


def get_previous_period(period: int) -> int:
    year = period // 100
    month = period % 100

    if month == 1:
        previous_period_year = year - 1
        previous_period_month = 12
    else:
        previous_period_year = year
        previous_period_month = month - 1

    previous_period = (previous_period_year * 100) + previous_period_month
    return previous_period


def get_period_range(start_period: int, end_period: int = None) -> list[int]:
    """
    Created by: Lucas Penha de Moura - 27/09/2024
        Creates randon date between two specified dates.

        This is very useful when creating test data mocks.
    :param start_period: the first period of the range
    :param end_period: the last period of the range
    :return: A list with all periods between start_period and end_period.
    """
    if not end_period:
        today = datetime.datetime.now(datetime.timezone.utc)
        end_period = today.year * 100 + today.month

    start_month = start_period % 100
    start_year = start_period // 100
    end_month = end_period % 100
    end_year = end_period // 100

    list_size = (end_year - start_year) * 12 + end_month - start_month
    period_list: list[int] = []
    for i in range(0, list_size + 1):
        period = start_year * 100 + start_month

        start_month += 1
        if start_month > 12:
            start_month = 1
            start_year += 1

        period_list.append(period)

    return period_list


def get_period_dates(period: int) -> tuple[datetime.date, datetime.date]:
    """
    Created by: Lucas Penha de Moura - 20/10/2024

    :param period:
    :return: The first and last date of the period.
    """
    year = period // 100
    month = period % 100

    first_day = datetime.datetime(year, month, 1)
    last_day = datetime.datetime(year, month, calendar.monthrange(year, month)[1])

    return first_day, last_day


def get_randon_date(start_date: datetime.date, end_date: datetime.date) -> datetime.date:
    """
    Created by: Lucas Penha de Moura - 06/10/2024
        Creates randon date between two specified dates.

        This is very useful when creating test data mocks.
    :param start_date:
    :param end_date:
    :return: A random date between two specified dates.
    """
    date_range = end_date - start_date
    random_days = random.randint(0, date_range.days)
    random_date = start_date + datetime.timedelta(days=random_days)

    return random_date
