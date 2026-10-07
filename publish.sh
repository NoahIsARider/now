#!/usr/bin/env sh
# Build and publish the now page to the ROOT of the sourcehut site.
#
# Token: a personal access token from https://meta.sr.ht/oauth2/personal-token
# with the scope  pages.sr.ht/PAGES:RW
# Read from $SRHT_TOKEN, else from ~/.srht-token, else asked for on the terminal.
#
# note: this uploads to the domain root. the films manifest lives in /MAYDAY/ and is
# published separately by its own publish.sh, into that subdirectory.
set -eu

cd "$(dirname "$0")"
DOMAIN="${SRHT_DOMAIN:-noahisarider.srht.site}"

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

echo "uploading $(du -h site.tar.gz | cut -f1) to $DOMAIN (root) ..."
curl -fsS -H "Authorization: Bearer $TOKEN" \
  -F "content=@site.tar.gz" \
  "https://pages.sr.ht/publish/$DOMAIN"
echo
echo "published -> https://$DOMAIN/"
