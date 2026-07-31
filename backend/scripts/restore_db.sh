#!/usr/bin/env bash
# Restores a MySQL dump (produced by backup_db.sh) into the running `db`
# service. DESTRUCTIVE — overwrites the current database contents. Run from
# the repo root:
#   ./backend/scripts/restore_db.sh path/to/backup.sql.gz [docker-compose-file]
set -euo pipefail

BACKUP_FILE="${1:-}"
COMPOSE_FILE="${2:-docker-compose.yml}"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file.sql.gz> [docker-compose-file]" >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo "Error: .env not found in the current directory — run this from the repo root." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a && source .env && set +a

echo "WARNING: this will overwrite all data in the '${MYSQL_DATABASE}' database"
echo "on the '${COMPOSE_FILE}' stack's db service, using ${BACKUP_FILE}."
read -r -p "Type the database name (${MYSQL_DATABASE}) to confirm: " CONFIRM
if [ "$CONFIRM" != "$MYSQL_DATABASE" ]; then
  echo "Confirmation did not match — aborting."
  exit 1
fi

echo "Restoring..."
gunzip -c "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T db \
  mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE}"

echo "Restore complete."
