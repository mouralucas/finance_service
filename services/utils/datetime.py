import datetime


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