
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/backup.log"
CONFIG_FILE="$SCRIPT_DIR/config.env"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

if [[ ! -f "$CONFIG_FILE" ]]; then
  log "ERROR: Missing config file: $CONFIG_FILE"
  exit 1
fi

# load config
source "$CONFIG_FILE"

: "${SOURCE_DIR:?SOURCE_DIR not set}"
: "${BACKUP_DIR:?BACKUP_DIR not set}"
: "${RETENTION_DAYS:?RETENTION_DAYS not set}"

if [[ ! -d "$SOURCE_DIR" ]]; then
  log "ERROR: SOURCE_DIR does not exist: $SOURCE_DIR"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

TS="$(date '+%Y%m%d_%H%M%S')"
ARCHIVE="$BACKUP_DIR/backup_${TS}.tar.gz"

log "Starting backup of $SOURCE_DIR"
tar -czf "$ARCHIVE" -C "$SOURCE_DIR" .
log "Backup created: $ARCHIVE"

log "Cleaning backups older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -type f -name "backup_*.tar.gz" -mtime +"$RETENTION_DAYS" -delete

log "Backup finished successfully"
exit 0

