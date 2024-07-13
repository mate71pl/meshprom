import json
from prometheus_client import start_http_server, Gauge
import time

# Define whether to delete old nodes
deleteOldNode = True  # Set to True or False

# Define metrics
battery_level = Gauge('battery_level', 'Battery level', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
voltage = Gauge('voltage', 'Voltage', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
channel_utilization = Gauge('channel_utilization', 'Channel utilization', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
air_util_tx = Gauge('air_util_tx', 'Air utilization Tx', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
uptime_seconds = Gauge('uptime_seconds', 'Uptime in seconds', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
snr = Gauge('snr', 'Signal to Noise Ratio', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
last_heard = Gauge('last_heard', 'Last Heard', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
latitude = Gauge('latitude', 'Latitude', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
longitude = Gauge('longitude', 'Longitude', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
altitude = Gauge('altitude', 'Altitude', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
hops_away = Gauge('hops_away', 'Hops Away', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
via_mqtt = Gauge('via_mqtt', 'Via MQTT', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])
is_licensed = Gauge('is_licensed', 'Is Licensed', ['device_id', 'long_name', 'short_name', 'macaddr', 'hw_model'])

def update_metrics(data):
    current_time = time.time()
    fifteen_minutes = 15 * 60

    for device_id, device_data in data.items():
        user = device_data.get('user', {})
        metrics = device_data.get('deviceMetrics', {})
        position = device_data.get('position', {})

        last_heard_time = device_data.get('lastHeard', 0)
        if deleteOldNode and (current_time - last_heard_time > fifteen_minutes):
            continue

        labels = {
            'device_id': device_id,
            'long_name': user.get('longName', ''),
            'short_name': user.get('shortName', ''),
            'macaddr': user.get('macaddr', ''),
            'hw_model': user.get('hwModel', '')
        }

        if 'batteryLevel' in metrics:
            battery_level.labels(**labels).set(float(metrics['batteryLevel']))
        if 'voltage' in metrics:
            voltage.labels(**labels).set(float(metrics['voltage']))
        if 'channelUtilization' in metrics:
            channel_utilization.labels(**labels).set(float(metrics['channelUtilization']))
        if 'airUtilTx' in metrics:
            air_util_tx.labels(**labels).set(float(metrics['airUtilTx']))
        if 'uptimeSeconds' in metrics:
            uptime_seconds.labels(**labels).set(float(metrics['uptimeSeconds']))
        if 'snr' in device_data:
            snr.labels(**labels).set(float(device_data['snr']))
        if 'lastHeard' in device_data:
            last_heard.labels(**labels).set(float(device_data['lastHeard']))
        if 'latitude' in position:
            latitude.labels(**labels).set(float(position.get('latitude', 0)))
        if 'longitude' in position:
            longitude.labels(**labels).set(float(position.get('longitude', 0)))
        if 'altitude' in position:
            altitude.labels(**labels).set(float(position.get('altitude', 0)))
        if 'hopsAway' in device_data:
            hops_away.labels(**labels).set(float(device_data['hopsAway']))
        if 'viaMqtt' in device_data:
            via_mqtt.labels(**labels).set(1.0 if device_data['viaMqtt'] else 0.0)
        if 'isLicensed' in user:
            is_licensed.labels(**labels).set(1.0 if user['isLicensed'] else 0.0)

if __name__ == '__main__':
    # Start HTTP server
    start_http_server(8000, addr="0.0.0.0")
    
    while True:
        try:
            # Read data from JSON file
            with open('/app/data.json', 'r') as file:
                data = file.read().strip()
                if data:
                    data = json.loads(data)
                    # Update metrics
                    update_metrics(data)
                else:
                    print("JSON file is empty.")
        except FileNotFoundError:
            print("JSON file does not exist.")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        # Wait 60 seconds before the next update
        time.sleep(60)

