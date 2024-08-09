#!/bin/bash

SERVICE_NAME="meshprom-org"

# Get the health status of the container
STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE_NAME)
if [ "$STATUS" == "unhealthy" ]; then
  echo "$(date '+%Y-%m-%d [%H:%M:%S] - Service $SERVICE_NAME restart!')" >> $HOME/docker/$SERVICE_NAME/healthcheck.log   
  docker restart "$SERVICE_NAME"
fi
## Add to crontab
##* * * * * /bin/bash /home/user/docker/meshprom/monitor.sh

