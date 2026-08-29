#!/usr/bin/env bash
# Deploy the resources site to https://alibuilds.blog/resources/
#
# Manual and deliberate, like WarmLine's deploy: no CI, no credentials on the
# box, no build step. Ships the static files over SSH into a read-only bind
# mount and verifies the live site answers.
#
# Usage:  ./scripts/deploy.sh            # ship + verify
#         ./scripts/deploy.sh --verify   # verify only, ship nothing
#
# Rollback: git checkout <sha> && ./scripts/deploy.sh
set -euo pipefail

HOST=warmline-box
REMOTE_ROOT=/srv/alibuilds-blog/html
BASE_URL=https://alibuilds.blog
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Only these are the site. deploy/, scripts/, design-options/ and the docs stay
# in git and never reach the box.
PAYLOAD=(index.html assets guides)

verify() {
  local fail=0 code
  check() {
    code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "$1" || echo 000)
    if [ "$code" = "$2" ]; then
      printf '  ok   %s  %s\n' "$code" "$1"
    else
      printf '  FAIL %s (want %s)  %s\n' "$code" "$2" "$1"
      fail=1
    fi
  }
  echo "verifying $BASE_URL"
  check "$BASE_URL/resources/" 200
  check "$BASE_URL/resources/assets/css/main.css" 200
  check "$BASE_URL/resources/guides/llm-council/" 200
  check "$BASE_URL/resources/nope-does-not-exist" 404
  # Bare host redirects to the site until the home page exists.
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "$BASE_URL/" || echo 000)
  case "$code" in
    302|301) printf '  ok   %s  %s/ -> /resources/\n' "$code" "$BASE_URL" ;;
    *)       printf '  FAIL %s (want 302)  %s/\n' "$code" "$BASE_URL"; fail=1 ;;
  esac
  return $fail
}

if [ "${1:-}" = "--verify" ]; then
  verify
  exit $?
fi

cd "$REPO_ROOT"
for p in "${PAYLOAD[@]}"; do
  [ -e "$p" ] || { echo "missing payload path: $p" >&2; exit 1; }
done

echo "shipping $(du -sh --exclude=.git "${PAYLOAD[@]}" 2>/dev/null | tail -1 | cut -f1) to $HOST:$REMOTE_ROOT/resources"

# Upload beside the live dir, then swap. The swap is two mv's, so there is a
# few-millisecond window where /resources does not exist.
# ponytail: good enough for a static site nobody is mid-transaction on. Upgrade
# path if it ever matters: serve through a symlink and swap the symlink (atomic).
ssh "$HOST" "rm -rf '$REMOTE_ROOT/resources.new' && mkdir -p '$REMOTE_ROOT/resources.new'"
tar -cf - "${PAYLOAD[@]}" | ssh "$HOST" "tar -C '$REMOTE_ROOT/resources.new' -xf -"
ssh "$HOST" "
  set -e
  chmod -R a+rX '$REMOTE_ROOT/resources.new'
  rm -rf '$REMOTE_ROOT/resources.old'
  [ -d '$REMOTE_ROOT/resources' ] && mv '$REMOTE_ROOT/resources' '$REMOTE_ROOT/resources.old'
  mv '$REMOTE_ROOT/resources.new' '$REMOTE_ROOT/resources'
  rm -rf '$REMOTE_ROOT/resources.old'
"

verify
