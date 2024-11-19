from rolf_common.backend.nosql_database import NoSqlDatabaseSessionManager

from backend.settings import settings

"""
    Create the NoSQL connection to save the logs
"""
mongo_session_manager = NoSqlDatabaseSessionManager(host=settings.log_database_url, db_name=settings.log_database_name)