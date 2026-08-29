#!/bin/sh
# Install to /usr/local/sbin/redeploy-resources.sh on warmline-box (root, 0755).
#
# Single source of truth for how the alibuilds-blog container runs. Always
# restart through this script — a bare `docker run` would drop the read-only
# mount or the capability drops. Mirrors redeploy-app.sh's role for WarmLine.
#
# Content is a read-only bind mount, so a content deploy does NOT need this
# script: scripts/deploy.sh swaps the files and nginx serves them immediately.
# Run this only to change how the container itself runs (image, flags, config).
set -eu

NAME=alibuilds-blog
IMAGE=nginxinc/nginx-unprivileged:1.27-alpine
SITE_ROOT=/srv/alibuilds-blog/html
NGINX_CONF=/srv/alibuilds-blog/nginx.conf

[ -d "$SITE_ROOT/resources" ] || { echo "missing $SITE_ROOT/resources" >&2; exit 1; }
[ -f "$NGINX_CONF" ] || { echo "missing $NGINX_CONF" >&2; exit 1; }

docker rm -f "$NAME" 2>/dev/null || true

docker run -d \
  --name "$NAME" \
  --network coolify \
  --restart unless-stopped \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --memory 128m \
  --pids-limit 128 \
  --log-opt max-size=10m --log-opt max-file=3 \
  -v "$NGINX_CONF":/etc/nginx/nginx.conf:ro \
  -v "$SITE_ROOT":/usr/share/nginx/html:ro \
  "$IMAGE"

# No published ports: Traefik reaches it over the coolify network only.
sleep 2
docker exec "$NAME" wget -qO- http://127.0.0.1:8080/healthz >/dev/null \
  && echo "$NAME up" \
  || { echo "$NAME failed health check" >&2; docker logs "$NAME" --tail 30; exit 1; }
