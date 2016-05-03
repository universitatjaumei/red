#!/bin/bash

DB="$HOME/red/data/db/red.db"
BACKUP_DIR="$HOME/red/dumps"
DATE=$(date +"%Y-%m-%d")

mkdir -p "$BACKUP_DIR"

sqlite3 "$DB" .dump | gzip -c > "$BACKUP_DIR/red.$DATE.dump.gz"

find "$BACKUP_DIR" -name "*.dump.gz" -mtime +30 -exec rm -f {} \;
