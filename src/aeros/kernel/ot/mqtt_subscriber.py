import json

import paho.mqtt.client as mqtt


def run_subscriber(topic: str = "areos/#", host: str = "localhost", port: int = 1883):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client, userdata, flags, reason_code, properties):
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        try:
            print(msg.topic, json.loads(payload))
        except json.JSONDecodeError:
            print(msg.topic, payload)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_forever()
