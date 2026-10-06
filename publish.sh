#!/usr/bin/env sh
# Build and publish MAYDAY to sourcehut pages.
#
# Token: a personal access token from https://meta.sr.ht/oauth2/personal-tokens
# with the scope  pages.sr.ht/PAGES:RW
# It is read from $SRHT_TOKEN, else from ~/.srht-token, else asked for on the terminal.
set -eu

cd "$(dirname "$0")"
DOMAIN="${SRHT_DOMAIN:-noahisarider.srht.site}"
SUBDIR="${SRHT_SUBDIR:-MAYDAY}"

TOKEN="${SRHT_TOKEN:-}"
if [ -z "$TOKEN" ] && [ -f "$HOME/.srht-token" ]; then
  TOKEN="$(tr -d '\r\n' < "$HOME/.srht-token")"
fi
if [ -z "$TOKEN" ]; then
  printf 'sr.ht personal access token (pages.sr.ht/PAGES:RW): '
  stty -echo 2>/dev/null || true
  read -r TOKEN
  stty echo 2>/dev/null || true
  printf '\n'
fi
if [ -z "$TOKEN" ]; then
  echo "no token, nothing published" >&2
  exit 1
fi

python build.py

rm -f site.tar.gz
tar -C site -czf site.tar.gz .

echo "uploading $(du -h site.tar.gz | cut -f1) to $DOMAIN/$SUBDIR ..."
curl -fsS -H "Authorization: Bearer $TOKEN" \
  -F "content=@site.tar.gz" \
  "https://pages.sr.ht/publish/$DOMAIN/$SUBDIR"
echo
echo "published -> https://$DOMAIN/$SUBDIR/"
