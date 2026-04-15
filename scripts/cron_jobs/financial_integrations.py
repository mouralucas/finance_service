import datetime
import time
import uuid

from backend.database import sessionmanager
from models.core import CronJobLogs
from scripts.crons import crons
from services.integration import BcbIntegrationService


@crons.cron("0 6 * * *", name="CDI daily sync")  # Runs daily at 6
async def sync_daily_data():
    async with sessionmanager.session() as session:
        t0 = time.time()
        sync_monthly = await BcbIntegrationService(session=session).sync_daily_data(
            indexer_id=uuid.UUID("2a2b100f-17d9-4c61-b3b4-f06662113953")
        )
        t1 = time.time()

        execution_time = datetime.timedelta(seconds=t1 - t0)

        cron_log = CronJobLogs(
            job_name="CDI daily sync",
            successful_run=sync_monthly.get("successful", False),
            entries_saved=sync_monthly.get("quantity"),
            exception=str(sync_monthly.get("exception", "")),
            execution_time=execution_time,
        )
        session.add(cron_log)


@crons.cron("0 5 1 * *", name="CDI monthly sync")  # Runs every first day of month at 5
async def sync_monthly_cdi():
    async with sessionmanager.session() as session:

        t0 = time.time()
        sync_monthly = await BcbIntegrationService(session=session).sync_monthly_data(
            indexer_id=uuid.UUID("2a2b100f-17d9-4c61-b3b4-f06662113953")
        )
        t1 = time.time()

        execution_time = datetime.timedelta(seconds=t1 - t0)

        cron_log = CronJobLogs(
            job_name="CDI monthly sync",
            successful_run=sync_monthly.get("successful", False),
            entries_saved=sync_monthly.get("quantity"),
            exception=str(sync_monthly.get("exception", "")),
            execution_time=execution_time,
        )
        session.add(cron_log)
