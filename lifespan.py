from rolf_common.backend.logger import set_log_handler
from rolf_common.backend.nosql_database import NoSqlDatabaseSessionManager, get_db_connection, set_db_connection
from rolf_common.managers.logs import BaseLogDataManager

from backend.settings import settings

# Instantiate the log database from Rolf Common
mongo_session_manager = NoSqlDatabaseSessionManager(host=settings.log_database_url, db_name=settings.log_database_name)


async def start_log_service():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        set_db_connection(mongo_session_manager)
        await get_db_connection().initialize()

        log_manager = BaseLogDataManager(get_db_connection(), collection_name=settings.log_collection_name)
        set_log_handler(log_manager)


async def shutdown_log_service():
    if settings.log_database_url is None and settings.log_database_name is None:
        return
    else:
        await mongo_session_manager.close()
