from backend.nosql_database import mongo_session_manager
from backend.settings import settings


async def start_log_database():
    if settings.log_database_url is None and settings.log_database_name is None:
        print('Log database not defined')
        return
    else:
        await mongo_session_manager.initialize()


async def shutdown_log_database():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        await mongo_session_manager.close()
