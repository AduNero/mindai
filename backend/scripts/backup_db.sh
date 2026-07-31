#!/usr/bin/env bash
# Dumps the MySQL database from the running `db` service to a timestamped
# file under backend/scripts/backups/. Run from the repo root:
#   ./backend/scripts/backup_db.sh [docker-compose-file]
set -euo pipefail

COMPOSE_FILE="${1:-docker-compose.yml}"
BACKUP_DIR="$(dirname "$0")/backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OUT_FILE="${BACKUP_DIR}/mindcare-${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

if [ ! -f .env ]; then
  echo "Error: .env not found in the current directory — run this from the repo root." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a && source .env && set +a

echo "Dumping ${MYSQL_DATABASE} from the '${COMPOSE_FILE}' stack's db service..."
docker compose -f "$COMPOSE_FILE" exec -T db \
  mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" \
  --single-transaction --routines --triggers "${MYSQL_DATABASE}" \
  | gzip > "$OUT_FILE"

echo "Backup written to ${OUT_FILE} ($(du -h "$OUT_FILE" | cut -f1))"
