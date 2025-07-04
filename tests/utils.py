import random
from datetime import datetime

from dateutil.relativedelta import relativedelta


def random_date(
        start_date: datetime = datetime.today() - relativedelta(days=100),
        end_date: datetime = datetime.today()
) -> datetime:
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)

    return start_date + relativedelta(days=random_days)
