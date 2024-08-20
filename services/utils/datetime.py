import datetime


def get_period(date: datetime.date | datetime.datetime) -> int:
    year = date.year
    month = date.month
    return year * 100 + month
