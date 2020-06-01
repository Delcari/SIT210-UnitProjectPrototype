import paho.mqtt.client as mqtt
from functools import partial
   
print('Successfully Loaded MQTT')

#Credentials
mqtt_username = "raspberrypi"
mqtt_password = "password"
mqtt_topic = "button"
mqtt_broker_ip = "192.168.0.131"

client = mqtt.Client()
# Set the username and password for the MQTT client
client.username_pw_set(mqtt_username, mqtt_password)

def on_connect(client, userdata, flags, rc):
    # rc is the error code returned when connecting to the broker
    print("Connected!", str(rc))

    # Once the client has connected to the broker, subscribe to the topic
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg, func):
    # Called everytime the topic is published to
    
    print("Topic: ", msg.topic + "\nMessage: " + str(msg.payload))
    func(int((str(msg.payload))[2:3]))

#Listening for messages to be published under the topic 'button'
def listening(func):
    client.on_connect = on_connect

    #sends the message to the GUI
    client.on_message = lambda *x: on_message(func=func, *x)
    
    client.connect(mqtt_broker_ip, 1883)


    client.loop_forever()
    client.disconnect()

