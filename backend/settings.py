from pydantic_settings import BaseSettings
from rolf_common.backend.settings import Settings


class FinanceSettings(Settings):
    # Project description
    project_name: str = "finance"
    project_title: str = "Finance Service"
    project_description: str = "Microservice for financial management"
    project_version: str = "0.0.1"

    # Database and test settings
    finance_database_url: str = 'postgresql+asyncpg://dev-user:password@localhost:5434/finance_dev_db'
    test_database_url: str = 'sqlite+aiosqlite:///:memory:'
    echo_sql: bool = False
    echo_test_sql: bool = True
    test: bool = False

    # Log database
    log_database_name: str = 'finance_dev_log'
    log_collection_name: str = 'finance_logs'
    log_database_url: str = 'mongodb://dev-user-logs:password@localhost:27017/finance_dev_log?authSource=admin'

    # Allowed origins CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:80,http://localhost"

settings = FinanceSettings()
