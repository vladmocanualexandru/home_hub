import random, time, psutil
from paho.mqtt import client as mqtt_client

def connect_mqtt(broker, username, password, port=1883):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(f'python-mqtt-{random.randint(0, 1000)}')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg):
    result = client.publish(topic, msg)

    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic}")

mqttClient = connect_mqtt("home.hub", "hass", "MOCdRicjNlkAdPC0VFRhRfqR3fXvpIP5G6WDN9FF4NsmlowRMXkpoovhX1N6jRKedmDEqoVmeAHniCierVqDEXeUuuZDSpgK6U53jXtknnuHBjBTA1ade9Fgw3wMIIOH")

while True:
    battery = psutil.sensors_battery()

    print("Laptop battery: %d" % battery.percent)
    publish(mqttClient, "homeassistant/sensor/laptopV", '{"battery":%d}' % battery.percent)
    time.sleep(30)