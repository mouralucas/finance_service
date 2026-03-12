from scripts.crons import crons


@crons.cron("* * * * *")  # Runs every day at midnight
async def sync_daily_data():
    print("Starting daily data synchronization for financial integrations...")
