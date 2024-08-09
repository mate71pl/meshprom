# MESHPROM
## A simple script for collecting information about [Meshtastic](https://meshtastic.org) nodes and presenting them in Prometheus Node-Exporter format.

## The script is in the testing phase!

### The script consists of two Docker containers.
 - **`node-device-stats`** - a virtual Meshtastic node is running inside, which exposes its API on the standard port 4403.
 - **`meshprom`** - inside, you'll find the [Meshtastic Python CLI](https://github.com/meshtastic/python), from which the output of the `meshtastic --listen` command is processed and made available in Prometheus Node-Exporter format.
  
To start using it, you need to build the images and run the containers:

```
docker compose up -d --build
```

To communicate with the node inside the container without exposing the API externally and using the local Meshtastic CLI, you can use the command:

```
docker exec meshprom meshtastic --host node-device-stats --export-config
```

Example Prometheus configuration:
```
scrape_configs:
  - job_name: 'node-exporter'
    scrape_interval: 60s
    static_configs:
      - targets: ['10.0.0.69:8000']
        labels:
          server: 'meshtastic-info'
```
