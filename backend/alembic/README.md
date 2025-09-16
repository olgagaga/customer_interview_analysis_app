# Alembic Migrations

- Create migration (autogen):
  - `alembic revision --autogenerate -m "init"`
- Apply migrations:
  - `alembic upgrade head`
- Downgrade:
  - `alembic downgrade -1` 