#!/usr/bin/env bash
# Export every English (lang='en') book from the vedabase.cc D1 database
# (vedabase-search-db) to one JSON file per book in /tmp/d1md/.
# Run from anywhere; needs wrangler authenticated for the astro_vedabase project.
set -euo pipefail

ASTRO="$HOME/git_projects/astro_vedabase"
DB="vedabase-search-db"
OUT="/tmp/d1md"
mkdir -p "$OUT"

cd "$ASTRO"

# Discover all books present for lang='en'.
BOOKS=$(npx wrangler d1 execute "$DB" --remote \
  --command "SELECT DISTINCT book FROM verses WHERE lang='en' ORDER BY book;" --json 2>/dev/null \
  | python3 -c "import sys,json;[print(x['book']) for x in json.load(sys.stdin)[0]['results']]")

for b in $BOOKS; do
  printf '  exporting %-12s ... ' "$b"
  npx wrangler d1 execute "$DB" --remote \
    --command "SELECT ref,book,devanagari,verse_text,synonyms,translation,purport FROM verses WHERE lang='en' AND book='$b';" \
    --json 2>/dev/null > "$OUT/$b.json"
  n=$(python3 -c "import json;print(len(json.load(open('$OUT/$b.json'))[0]['results']))")
  printf '%s rows\n' "$n"
done
echo "Done. JSON in $OUT/"
