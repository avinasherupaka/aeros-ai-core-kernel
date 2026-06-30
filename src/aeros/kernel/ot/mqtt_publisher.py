"""
MQTT publisher for Areos UNS messages.

Local equivalent of publishing to AWS IoT Core MQTT topics.
Wraps paho-mqtt and serialises SparkplugInspiredEnvelope payloads.

Usage (from code):
    publisher = MQTTPublisher()
    publisher.publish(topic, envelope)

    # or batch:
    publisher.publish_many(topic, envelopes)

The broker must be running (e.g. `docker compose up mqtt`).
"""

import json

import paho.mqtt.client as mqtt

from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope


class MQTTPublisher:
    def __init__(self, host: str = "localhost", port: int = 1883, qos: int = 1):
        self.host = host
        self.port = port
        self.qos = qos
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def publish(self, topic: str, envelope: SparkplugInspiredEnvelope) -> None:
        """Connect, publish one message, disconnect."""
        self.client.connect(self.host, self.port, 60)
        payload = envelope.model_dump_json()
        self.client.publish(topic, payload=payload, qos=self.qos)
        self.client.disconnect()

    def publish_many(self, topic: str, envelopes: list[SparkplugInspiredEnvelope]) -> None:
        """Connect once, publish a batch of envelopes, disconnect."""
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()
        for envelope in envelopes:
            payload = envelope.model_dump_json()
            self.client.publish(topic, payload=payload, qos=self.qos)
        self.client.loop_stop()
        self.client.disconnect()
