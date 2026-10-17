#!/usr/bin/env sh
# Build the whole site and publish it to the sourcehut pages root.
#
# Token: a personal access token from https://meta.sr.ht/oauth2/personal-token
# with the scope  pages.sr.ht/PAGES:RW
# Read from $SRHT_TOKEN, else from ~/.srht-token, else asked for on the terminal.
#
# One build now produces everything: the now page, the papers page, the MAYDAY
# films manifest under /MAYDAY/ and the shkb records manifest under /shkb/. One
# tarball, one upload, so there is no root-wipes-the-subdirectory problem left.
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

# the build prints its output paths, which are not cp1252-safe on Windows
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

python build.py

rm -f site.tar.gz
tar -C site -czf site.tar.gz .

echo "uploading $(du -h site.tar.gz | cut -f1) to $DOMAIN (root, including /MAYDAY/ and /shkb/) ..."
curl -fsS -H "Authorization: Bearer $TOKEN" \
  -F "content=@site.tar.gz" \
  "https://pages.sr.ht/publish/$DOMAIN"
echo
echo "published -> https://$DOMAIN/"
