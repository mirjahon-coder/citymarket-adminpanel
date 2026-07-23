# City Market server deploy

This setup runs the Vue frontend and FastAPI backend from one server IP. Nginx serves the frontend and forwards `/api/*` requests to FastAPI.

## 1. Prepare environment on the server

Clone the repository, then create `backend/.env` from the example:

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Set real values. Do not commit this file:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SESSION_SECRET=replace-with-a-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-strong-password
CORS_ORIGINS=http://SERVER_IP
```

`DATABASE_URL` can point to an external managed PostgreSQL database. The application does not create a database container.

## 2. Start the application

Install Docker and Docker Compose on the server, then run:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

Open `http://SERVER_IP` in a browser. The API health check is available at `http://SERVER_IP/api/health` and the Swagger docs at `http://SERVER_IP/docs`.

## 3. Update after a GitHub push

```bash
git pull origin main
docker compose up -d --build
```

The frontend uses relative `/api` requests, so no frontend API URL needs to be changed for an IP-only deployment.

## Security checklist

- Never commit `backend/.env`.
- Rotate any database password that has already been exposed locally.
- Use a long random `SESSION_SECRET`.
- Change `ADMIN_PASSWORD` before the first production start.
- Add HTTPS later with a domain and a reverse proxy such as Caddy or Nginx.