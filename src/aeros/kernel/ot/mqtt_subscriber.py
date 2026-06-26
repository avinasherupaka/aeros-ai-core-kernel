"""
MQTT subscriber for Areos UNS messages.

Local equivalent of subscribing to AWS IoT Core MQTT topics.
Prints received payloads to stdout; extend on_message to forward to
the event router, state-of-control engine, or local storage.

Usage:
    python -m aeros.kernel.ot.mqtt_subscriber

The broker must be running (e.g. `docker compose up mqtt`).
"""

import json

import paho.mqtt.client as mqtt


def run_subscriber(topic: str = "areos/#", host: str = "localhost", port: int = 1883):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"[subscriber] Connected to {host}:{port} — subscribing to '{topic}'")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        try:
            data = json.loads(payload)
            print(f"[{msg.topic}] {json.dumps(data, default=str)}")
        except json.JSONDecodeError:
            print(f"[{msg.topic}] {payload}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    print(f"[subscriber] Waiting for messages on '{topic}' …  (Ctrl-C to stop)")
    client.loop_forever()


if __name__ == "__main__":
    run_subscriber()
