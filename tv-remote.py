import paho.mqtt.client as paho
import json, time, threading
from subprocess import call

mqtt_server      = "192.168.0.2"
mqtt_port        = 1883

# device credentials
device_id        = 'tv_remote'      # * set your device id (will be the MQTT client username)
device_secret    = ''  # * set your device secret (will be the MQTT client password)
random_client_id = ''  # * set a random client_id (max 23 char)

# device topics
in_topic  = 'devices/' + device_id + '/command'  # receiving messages
out_topic = 'devices/' + device_id + '/set'  # publishing messages

# --------------- #
# Callback events #
# --------------- #

# connection event
def on_connect(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))
    client.subscribe(in_topic, 0)                     # MQTT subscribtion (with QoS level 0)

# subscription event
def on_subscribe(client, userdata, mid, gqos):
    print('Subscribed: ' + str(mid))

# received message event
def on_message(client, obj, msg):
    # get the JSON message
    value = msg.payload
    # lirc
    #if value == 'power':
        #call(['/usr/bin/irsend', 'SEND_ONCE', 'BN59-01039A', 'power'])
    if value == 'on':
        value = "KEY_POWER"
    call(['/usr/bin/irsend', 'SEND_ONCE', 'Panasonic_EUR7613Z6A', value])
    #call(['/usr/bin/irsend', 'SEND_ONCE', 'BN59-01039A', value])

    # confirm changes to mqtt
    client.publish(out_topic, value)

# ------------- #
# Wait for net  #
# ------------- #

def wait_net_service(server, port):
    """ Wait for network service to appear 
        @return: True of False, if timeout is None may return only True or
                 throw unhandled network exception
    """
    import socket
    import errno
    import time

    s = socket.socket()

    while True:
        try:
            s.connect((server, port))
            time.sleep(1)
        
        except socket.error, err:
            # catch timeout exception from underlying network library
            if False and (type(err.args) != tuple or err[0] != errno.ETIMEDOUT):
                raise
        else:
            s.close()
            return True

# ------------- #
# MQTT settings #
# ------------- #

# create the MQTT client
client = paho.Client(client_id=random_client_id, protocol=paho.MQTTv31)  # * set a random string (max 23 chars)

# assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_subscribe = on_subscribe

wait_net_service(mqtt_server, mqtt_port)

# client connection
client.username_pw_set(device_id, device_secret)  # MQTT server credentials
client.connect(mqtt_server)                   # MQTT server address

client.loop_forever()

