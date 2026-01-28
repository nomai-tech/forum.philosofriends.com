# forum.philosofriends.com

A lightweight Django forum for short, sincere questions about meaning, mind, and ethics.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Seed demo content:

```bash
python manage.py seed_demo
```

## Deploy (k3s)

This repo includes a Helm chart in `deploy/web-app` and default values in `deploy/philo-news-values.yaml`.
The chart supports a PVC for sqlite and an nginx sidecar to serve `/static/`.

Typical deployment:

```bash
docker build -t <image>:<tag> .
docker push <image>:<tag>

helm upgrade --install forum deploy/web-app \
  -n jon \
  -f deploy/philo-news-values.yaml \
  --set image.name=<image>:<tag> \
  --set ingress.host=forum.philosofriends.com
```

## Notes

- Production uses `uvicorn` via the Helm `command`/`args` values.
- `DATABASE_PATH` controls sqlite location; for k3s it is mounted at `/data/db.sqlite3`.
- Set `POSTGRES_HOST/POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD` or `DATABASE_URL` to use Postgres instead of sqlite.
