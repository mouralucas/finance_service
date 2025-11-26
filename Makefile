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
apply-migrations:
	$(PYTHON) -m $(ALEMBIC) $(COMMAND_UPGRADE)

create-db-migration:
	@read -p "Type the migration message: " msg; \
	python3 -m alembic.config revision --autogenerate -m "$$msg"

# Create basic data in docker database
insert-data:
	source venv/bin/activate && $(PYTHON) populate-database.py


# Lint GraphQL schema files (requires node/npm). Uses npx so installation isn't mandatory
lint-graphql:
	npx graphql-schema-linter 'schemas_graphql/**/*.graphql'