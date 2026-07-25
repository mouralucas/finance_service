# AGENTS.md

## Project

API to personal finance manager

This API backend is build in Python using FastAPI, SQLAlchemy 2.0 async and GraphQL. 

## Architecture

- Use SQLAlchemy 2.0 with athe API `select()`, `delete()`, etc.
- Always use AsyncSession.
- Never create sync fetches.
- Never use ORM Query (`session.query()`).
- All business logic belongs to Service layer.
- GraphQL resolver only validate inputs and call Services

## Convertions

- All Models ends with `Model`.
- All Services ends with `Service`.
- All Managers ends with `Manager`.
- Dates uses `datetime.date`.
