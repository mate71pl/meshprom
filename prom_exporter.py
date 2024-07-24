import json
from prometheus_client import start_http_server, Gauge
import time
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 
IgnoreNodesWithoutMAC = True 
DelOldNode = True 
# Define timeout for ignoring old nodes (in minutes)
node_timeout_minutes = 15  # Set to desired number of minutes
node_timeout_seconds = node_timeout_minutes * 60

# Define metrics with the correct label order
metrics = {
    'battery_level': Gauge('battery_level', 'Battery level', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'voltage': Gauge('voltage', 'Voltage', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'channel_utilization': Gauge('channel_utilization', 'Channel utilization', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'air_util_tx': Gauge('air_util_tx', 'Air utilization Tx', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'uptime_seconds': Gauge('uptime_seconds', 'Uptime in seconds', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'snr': Gauge('snr', 'Signal to Noise Ratio', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'last_heard': Gauge('last_heard', 'Last Heard', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'latitude': Gauge('latitude', 'Latitude', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'longitude': Gauge('longitude', 'Longitude', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'altitude': Gauge('altitude', 'Altitude', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'hops_away': Gauge('hops_away', 'Hops Away', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'via_mqtt': Gauge('via_mqtt', 'Via MQTT', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr']),
    'is_licensed': Gauge('is_licensed', 'Is Licensed', ['device_id', 'long_name', 'short_name', 'hw_model', 'macaddr'])
}

def get_meshtastic_data():
    try:
        result = subprocess.run(
            ["meshtastic", "--host", "node-device-stats", "--info"],
            capture_output=True, text=True, check=True
        )
        output = result.stdout
        nodes_data = extract_nodes_data(output)
        return nodes_data
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing meshtastic command: {e}")
        return None

def extract_nodes_data(output):
    start_marker = "Nodes in mesh:"
    end_marker = "Preferences:"

    try:
        start_index = output.index(start_marker) + len(start_marker)
        end_index = output.index(end_marker)
        nodes_section = output[start_index:end_index].strip()
        
        # Remove leading and trailing braces and fix formatting
        nodes_section = nodes_section.strip('{}').strip()
        if nodes_section.endswith(','):
            nodes_section = nodes_section[:-1]
        
        nodes_section = '{' + nodes_section + '}'
        
        return json.loads(nodes_section)
    except (ValueError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing nodes data: {e}")
        logging.debug(f"Nodes data content: {nodes_section}")
        return None

def clear_old_metrics(labels):
    for metric in metrics.values():
        try:
            metric.remove(*labels.values())
        except KeyError:
            pass

def update_metrics(data):
    current_time = time.time()

    for device_id, device_data in data.items():
        user = device_data.get('user', {})
        metrics_data = device_data.get('deviceMetrics', {})
        position = device_data.get('position', {})

        # Skip nodes without a MAC address if IgnoreNodesWithoutMAC is set to True
        if IgnoreNodesWithoutMAC and not user.get('macaddr'):
            continue

        last_heard_time = device_data.get('lastHeard', None)
        if last_heard_time is None or (DelOldNode and (current_time - last_heard_time > node_timeout_seconds)):
            labels = {
                'device_id': device_id,
                'long_name': user.get('longName', ''),
                'short_name': user.get('shortName', ''),
                'hw_model': user.get('hwModel', ''),
                'macaddr': user.get('macaddr', '')
            }
            clear_old_metrics(labels)
            continue

        labels = {
            'device_id': device_id,
            'long_name': user.get('longName', ''),
            'short_name': user.get('shortName', ''),
            'hw_model': user.get('hwModel', ''),
            'macaddr': user.get('macaddr', '')
        }

        logging.info(f"Updating metrics for device: {device_id}")

        # Update gauges with available metrics
        if 'batteryLevel' in metrics_data:
            metrics['battery_level'].labels(**labels).set(metrics_data['batteryLevel'])
        if 'voltage' in metrics_data:
            metrics['voltage'].labels(**labels).set(metrics_data['voltage'])
        if 'channelUtilization' in metrics_data:
            metrics['channel_utilization'].labels(**labels).set(metrics_data['channelUtilization'])
        if 'airUtilTx' in metrics_data:
            metrics['air_util_tx'].labels(**labels).set(metrics_data['airUtilTx'])
        if 'uptimeSeconds' in metrics_data:
            metrics['uptime_seconds'].labels(**labels).set(metrics_data['uptimeSeconds'])
        if 'snr' in device_data:
            metrics['snr'].labels(**labels).set(device_data['snr'])
        if 'lastHeard' in device_data:
            metrics['last_heard'].labels(**labels).set(device_data['lastHeard'])
        if 'latitude' in position:
            metrics['latitude'].labels(**labels).set(position['latitude'])
        if 'longitude' in position:
            metrics['longitude'].labels(**labels).set(position['longitude'])
        if 'altitude' in position:
            metrics['altitude'].labels(**labels).set(position['altitude'])
        if 'hopsAway' in device_data:
            metrics['hops_away'].labels(**labels).set(device_data['hopsAway'])
        if 'viaMqtt' in device_data:
            metrics['via_mqtt'].labels(**labels).set(1.0 if device_data['viaMqtt'] else 0.0)
        if 'isLicensed' in user:
            metrics['is_licensed'].labels(**labels).set(1.0 if user['isLicensed'] else 0.0)

if __name__ == '__main__':
    # Start HTTP server
    start_http_server(8000, addr="0.0.0.0")
    
    while True:
        data = get_meshtastic_data()
        if data:
            update_metrics(data)
        else:
            logging.warning("Failed to get data from Meshtastic")
        
        # Wait 60 seconds before the next update
        time.sleep(60)

