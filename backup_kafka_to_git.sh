#!/bin/bash
# filepath: /home/sd22750/kafka_sentiment_pipeline/backup_kafka_to_git.sh

set -e

cd /home/sd22750/kafka_sentiment_pipeline
# CONFIG
CONTAINER=wordpress
BACKUP_DIR=/home/sd22750/wp-backup
GIT_BRANCH=main

## Check for changes
if git status --porcelain | grep .; then
  git add .
  git commit -m "Automated backup: $(date '+%Y-%m-%d %H:%M')"
  git push origin main
  echo "Backup committed and pushed."
else
  echo "No changes detected. No backup needed."
fi