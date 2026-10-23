#!/bin/sh
# Rebuild the book and publish ONLY the built page to Cloudflare Pages.
# The repo itself stays private; the site is public at the URL below.
set -e
cd "$(dirname "$0")"
python3 build.py
SITE=$(mktemp -d)
cp python-course.html "$SITE/index.html"
npx --yes wrangler@3 pages deploy "$SITE" --project-name=python-from-zero --branch=main --commit-dirty=true
echo "Live: https://python-from-zero-74f.pages.dev"
