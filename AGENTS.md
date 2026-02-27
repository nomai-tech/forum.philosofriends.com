## Deployment note

Always deploy using the local Helm chart and values file so persistence, env vars (ALLOWED_HOSTS/CSRF), and uvicorn/asgi are enabled:

1) Build and push the image to `pdr.jonbesga.com`.
2) Deploy with:
   `helm upgrade --install forum deploy/web-app -n jon -f deploy/philo-news-values.yaml --set image.name=<image>:<tag> --set containerPort=8000 --set service.targetPort=8000`

## Deployment pitfalls (learned Feb 2026)

- **Image name convention**: use `pdr.jonbesga.com/forum.philosofriends.com:<sha>` — NOT `pdr.jonbesga.com/philosofriends-com:<sha>`.
- **Always use the local chart and values file** (`deploy/web-app` + `deploy/philo-news-values.yaml`) as documented above. Do NOT use the remote chart URL.
- **Do not pass `--set ingress.host=...`** for forum deploys; that can override/alter multi-host rules. Keep both hosts in `deploy/philo-news-values.yaml`.
- **containerPort must be 8000** — Django listens on 8000, not 80. If deploying with overrides, pass `--set containerPort=8000 --set service.targetPort=8000`.
- **There is a separate `philosofriends-com` Helm release** for `philosofriends.com` (a different site) in the same `jon` namespace. Do NOT touch it when deploying this forum.
- **Use `uv run python manage.py`** for all Django management commands. The `.venv` is Python 3.14.
- **Run migrations locally** with `uv run python manage.py migrate` before testing after pulling new code.

## Current architecture notes (Jan 2026)

### Database migration
- Production DB migrated from sqlite to Postgres (default namespace).
- App now uses Postgres when `DATABASE_URL` or `POSTGRES_*` env vars are set; sqlite is fallback.
- Postgres connection is configured via Helm values; password is sourced from a Kubernetes Secret (do NOT store secrets in this repo).
- `psycopg2-binary` is required and included in `requirements.txt`.

### Helm values and runtime env
- `deploy/philo-news-values.yaml` now sets Postgres env vars and pulls `POSTGRES_PASSWORD` from secret `forum-postgres`.
- `PASSWORD_HASHER_ITERATIONS` is configurable via env and currently set low for performance testing (value is in Helm values).
- App resources: requests are low to fit the single-node cluster; limits are higher for burst.
- PVC for sqlite is disabled (persistence off); Postgres is now the durable store.

### Safety / secrets
- Do not commit passwords or tokens to the repo.
- If you need Postgres credentials, use the Kubernetes secret `forum-postgres` in namespace `jon`.
