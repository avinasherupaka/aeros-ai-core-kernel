import json

import paho.mqtt.client as mqtt

from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope


class MQTTPublisher:
    def __init__(self, host: str = "localhost", port: int = 1883):
        self.host = host
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def publish(self, topic: str, envelope: SparkplugInspiredEnvelope) -> None:
        self.client.connect(self.host, self.port, 60)
        payload = envelope.model_dump_json()
        self.client.publish(topic, payload=payload, qos=0)
        self.client.disconnect()
