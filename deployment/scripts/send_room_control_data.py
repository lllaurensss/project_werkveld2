import json
import sys
import time

import paho.mqtt.client as mqtt

temperature = float(sys.argv[1])
room_control_data = {"temperature": temperature, "kp": 0.85, "kd": 0.15}


broker_address = "localhost"
broker_port = 1883
mqtt_topic = "/LP_ENVIROSENSE_APP/set_desired_temp/"

client = mqtt.Client()
client.connect(broker_address, broker_port)

client.loop_start()
payload = json.dumps(room_control_data)
client.publish(mqtt_topic, payload)
time.sleep(0.5)
client.loop_stop()

client.disconnect()
