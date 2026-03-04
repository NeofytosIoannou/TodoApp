# TodoApp (FastAPI)

## Deploy on Render with SQLite

This app supports SQLite in production **if you use a persistent disk**.

### 1) Add a persistent disk
- In Render, open your Web Service.
- Add a Disk.
- Mount path: `/var/data`

### 2) Set environment variables
Use these in Render Environment:

- `DATABASE_URL=sqlite:////var/data/todosapp.db`
- `SECRET_KEY=<your-long-random-secret>`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_MINUTES=20`
- `AUTH_COOKIE_NAME=access_token`
- `COOKIE_SECURE=true`
- `COOKIE_SAMESITE=lax`

### 3) Deploy
- Redeploy your service after setting env vars.

### 4) Verify persistence
1. Open `/healthy`.
2. Create a todo.
3. Redeploy/restart the service.
4. Confirm the todo still exists.

If data disappears after restart, check that the disk is mounted at `/var/data` and `DATABASE_URL` matches exactly.
