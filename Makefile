# Use bash as the shell
SHELL := /bin/bash

# Define the Python interpreter and the Alembic command
VENV_PATH = venv
PYTHON = python3
ALEMBIC = alembic.config
COMMAND_UPGRADE = upgrade head

# Default target
all: insert-data

# Run the Alembic upgrade command
upgrade-database:
	source venv/bin/activate && $(PYTHON) -m $(ALEMBIC) $(COMMAND_UPGRADE)


# Create basic data in docker database
insert-data:
	source venv/bin/activate && $(PYTHON) populate-database.py