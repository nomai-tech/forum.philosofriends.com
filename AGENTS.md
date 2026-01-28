## Deployment note

Always deploy using the local Helm chart and values file so persistence, env vars (ALLOWED_HOSTS/CSRF), and uvicorn/asgi are enabled:

1) Build and push the image to `pdr.jonbesga.com`.
2) Deploy with:
   `helm upgrade --install forum deploy/web-app -n jon -f deploy/philo-news-values.yaml --set image.name=<image>:<tag> --set ingress.host=forum.philosofriends.com`

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

### Postgres resources
- Postgres statefulset in `default` namespace has higher resources than before:
  - requests: 500m CPU / 1Gi
  - limits: 1 CPU / 2Gi

### Known fixes/behavior
- Logout uses a custom GET handler (`/accounts/logout/`) instead of Django’s POST-only LogoutView.
- Login performance inside Django is fast (<100ms) after rehashing; any remaining slowness likely comes from ingress/network.

### Ops changes made
- Removed pgAdmin (Helm release + PVC deleted) to free resources.
- ai-sticker-api (in `ai-stickers` namespace) resources were reduced and replicas scaled to 1 (current live state).

### Safety / secrets
- Do not commit passwords or tokens to the repo.
- If you need Postgres credentials, use the Kubernetes secret `forum-postgres` in namespace `jon`.
