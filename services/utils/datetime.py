import calendar
import random
from datetime import UTC, date, datetime, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta


def get_current_period():
    today = datetime.now(UTC)
    month = today.month
    year = today.year

    return year * 100 + month


def get_period(reference_date: date | datetime) -> int:
    # TODO: add support for str param
    year = reference_date.year
    month = reference_date.month
    return year * 100 + month


# def get_previous_period(period: int) -> int:
#     year = period // 100
#     month = period % 100
#
#     if month == 1:
#         previous_period_year = year - 1
#         previous_period_month = 12
#     else:
#         previous_period_year = year
#         previous_period_month = month - 1
#
#     previous_period = (previous_period_year * 100) + previous_period_month
#     return previous_period


def get_previous_period(period: int = get_current_period(), offset: int = 1) -> int:
    """
    Created by: Lucas Penha de Moura - 25/10/2024
        Returns the previous period based in the offset
    :param period: the base period
    :param offset: how many periods back is the wanted period
    :return:
    """
    month = period % 100
    year = period // 100
    for i in range(offset):
        month -= 1
        if month < 1:
            month = 12
            year -= 1

    return year * 100 + month


def get_period_range(start_period: int, end_period: int | None = None) -> list[int]:
    """
    Created by: Lucas Penha de Moura - 27/09/2024
        Creates randon date between two specified dates.

        This is very useful when creating test data mocks.
    :param start_period: the first period of the range
    :param end_period: the last period of the range
    :return: A list with all periods between start_period and end_period.
    """
    if not end_period:
        today = datetime.now(UTC)
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


def get_period_dates(period: int) -> tuple[date, date]:
    """
    Created by: Lucas Penha de Moura - 20/10/2024

    :param period:
    :return: The first and last date of the period.
    """
    year = period // 100
    month = period % 100

    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    return first_day, last_day


def get_randon_date(start_date: date, end_date: date) -> date:
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
    random_date = start_date + timedelta(days=random_days)

    return random_date


def get_installments_due_dates(transaction_date: date, close_day: int, due_day: int,
                               tot_installments: int = 1, return_str: bool = False) -> list[date | Any]:
    month = transaction_date.month
    year = transaction_date.year

    if transaction_date.day >= close_day:
        # If bill is already closed, the charge will be set in next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    if close_day > due_day:
        month += 1
        if month > 12:
            month = 1
            year += 1

    installments_due_dates = []
    for i in range(1, tot_installments + 1):
        due_date = datetime(year, month, due_day)
        if i > 1:
            due_date += relativedelta(months=i - 1)
        installments_due_dates.append(
            {
                'current_installment': i,
                'due_date': due_date.date()
            }
        )

    if return_str:
        pass

    return installments_due_dates
