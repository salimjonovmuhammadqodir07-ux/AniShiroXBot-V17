#!/usr/bin/env bash
# Foydalanish: ./scripts/backup.sh
# DATABASE_URL .env fayldan yoki muhit o'zgaruvchisidan olinadi.
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUT_DIR="./backups"
mkdir -p "$OUT_DIR"

if [ -z "${DATABASE_URL:-}" ]; then
  export $(grep -v '^#' .env | xargs)
fi

pg_dump "$DATABASE_URL" > "$OUT_DIR/anishiroxbot_${TIMESTAMP}.sql"
echo "Backup saqlandi: $OUT_DIR/anishiroxbot_${TIMESTAMP}.sql"
