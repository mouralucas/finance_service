from backend.database import sessionmanager
from models.core import CronJobLogs
from scripts.crons import crons


@crons.cron("0 5 * * *")  # Runs every day at 5
async def sync_daily_data():
    print("Starting daily CDI integration")


# @crons.cron("0 5 1 * *", name="CDI monthly sync") # Runs every first day of month at 5
@crons.cron("* * * * *")
async def sync_monthly_cdi():
    print("testing log")
    async with sessionmanager.session() as session:
        cron_log = CronJobLogs(
            job_name="Testing saving logs",
            successful_run=True,
        )
        session.add(cron_log)
