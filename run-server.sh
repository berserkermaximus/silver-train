export DB_URL=postgresql://postgres:user@127.0.0.1:5432/bitespeed
uvicorn app.server:api --port 9061 --reload