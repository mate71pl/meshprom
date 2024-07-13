#!/bin/bash

# Pętla do tworzenia pliku data.json co minutę
while true; do
    docker exec mmrelaynode-app meshtastic --host mmrelaydevice --info | awk '/Nodes in mesh:/ {flag=1; next} /Preferences:/ {flag=0} flag' | sed '1s/^/{/; $s/,$/}/' > data.json
    sleep 60
done

