import random, time, psutil, os
from paho.mqtt import client as mqtt_client

def connect_mqtt(broker, username, password, port=1883):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(f'laptopv-{random.randint(0, 1000)}')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg):
    result = client.publish(topic, msg)

    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic} ({status})")

# Ensure the broker is reachable
PING_ATTEMPTS = 60

brokerReachable = False
for a in range(PING_ATTEMPTS):
    response = os.system("ping -n 1 " + os.getenv('MQTT_BROKER'))

    if response == 0:
        print("Broker reachable!")
        brokerReachable = True
        break
    else:
        print ('Ping to ',os.getenv('MQTT_BROKER'), 'failed. Attempt=', a)

    time.sleep(1)

if not brokerReachable:
    print("Unable to reach broker.")
    exit(1)

mqttClient = connect_mqtt(os.getenv('MQTT_BROKER'), os.getenv('MQTT_USER'), os.getenv('MQTT_PASSWORD'))

while True:
    batteryPercent = psutil.sensors_battery().percent
    # batteryPercent = random.randint(0,100)

    # print("Laptop battery: %d" % batteryPercent)
    publish(mqttClient, os.getenv('MQTT_LAPTOPV_BATTERY_TOPIC'), '{"battery":%d}' % batteryPercent)
    time.sleep(90)