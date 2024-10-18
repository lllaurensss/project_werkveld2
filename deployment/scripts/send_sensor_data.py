import json
import sys
import time

import paho.mqtt.client as mqtt

temperature = float(sys.argv[1])
sensor_data = {"id": "bea83a3b-3034-476f-8451-a2677a4ffc3c", "temperature": temperature, "humidity": 85.1, "pressure": 966.18, "timestamp": "2024-10-18 14:38:23.343361"}


broker_address = "localhost"
broker_port = 1883
mqtt_topic = "/LP_ENVIROSENSE_APP/sensor_data/"

client = mqtt.Client()
client.connect(broker_address, broker_port)

client.loop_start()
payload = json.dumps(sensor_data)
client.publish(mqtt_topic, payload)
time.sleep(0.5)
client.loop_stop()

client.disconnect()