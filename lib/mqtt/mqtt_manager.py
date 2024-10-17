from logging import Logger
import paho.mqtt.client as mqtt
from queue import Queue


class MQTTManager:
    def __init__(self, broker_address="localhost", port=1883, keepalive=60, logger: Logger = None, message_list: Queue = Queue()):
        self._broker_address = broker_address
        self._port = port
        self._keepalive = keepalive
        self._client = mqtt.Client()
        self._logger = logger or Logger(__name__)
        self._message_list = message_list

        # MQTT Callbacks
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """Callback when the client connects to the broker."""
        if rc == 0:
            self._logger.info("Connected to MQTT Broker!")
        else:
            self._logger.warning(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """Callback when a message is received from the broker."""
        self._logger.info(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}' with QoS {msg.qos}")

        message = msg.payload.decode()

        self._message_list.put({
            'topic': msg.topic,
            'payload': message,
            'qos': msg.qos
        })

    def connect(self):
        """Connect to the MQTT broker."""
        self._client.connect(self._broker_address, self._port, self._keepalive)
        self._client.loop_start()  # Starts a new thread to process network traffic
        self._logger.info(f"Attempting to connect to MQTT broker at {self._broker_address}:{self._port}")

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self._client.loop_stop()  # Stop the loop
        self._client.disconnect()
        self._logger.info("Disconnected from MQTT Broker.")

    def subscribe(self, topic, qos=0):
        """Subscribe to a specific topic."""
        self._client.subscribe(topic, qos=qos)
        self._logger.info(f"Subscribed to topic '{topic}' with QoS {qos}")

    def unsubscribe(self, topic):
        """Unsubscribe from a specific topic."""
        self._client.unsubscribe(topic)
        self._logger.info(f"Unsubscribed from topic '{topic}'")

    def publish(self, topic, payload, qos=0, retain=False):
        """Publish a message to a specific topic."""
        self._client.publish(topic, payload, qos=qos, retain=retain)
        self._logger.info(f"Published message '{payload}' to topic '{topic}' with QoS {qos}")
