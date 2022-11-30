import paho.mqtt.client as mqtt
import json, os, time

def handle_command(command):
    if command == 'shutdown':
        os.system("shutdown /s /f /t 0")
        exit(1)
    if command == 'test':
        print('TEST')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(os.getenv('MQTT_TOPIC'))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    handle_command(payload['command'])
    # print(msg.topic+" "+str(msg.payload))

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

# Connect to mqtt broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PASSWORD'))

client.connect(os.getenv('MQTT_BROKER'), int(os.getenv('MQTT_PORT')), 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
