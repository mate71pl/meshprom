#!/bin/bash

# Uruchomienie skryptu update_data.sh w tle
./update_data.sh &

# Uruchomienie eksportera metryk
python prom_exporter.py
