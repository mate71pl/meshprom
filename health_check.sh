#!/bin/bash

# File that contains the last update time
LAST_UPDATE_FILE="/app/last_update_time.txt"

# Check if the file exists
if [ ! -f "$LAST_UPDATE_FILE" ]; then
  echo "Health check failed. Last update file not found. Restarting the container..."
  exit 1
fi

# Get the current timestamp
current_time=$(date +%s)

# Get the last update timestamp from the file
last_update_time=$(cat "$LAST_UPDATE_FILE")

# Check if the last update time is older than 3 minutes (180 seconds)
if [ $(($current_time - $last_update_time)) -gt 180 ]; then
  echo "Health check failed. Last update was more than 3 minutes ago. Restarting the container..."
  exit 1
else
  echo "Health check passed."
  exit 0
fi

