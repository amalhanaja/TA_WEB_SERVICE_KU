import datetime
import json
import paho.mqtt.client as mqtt
import psycopg2

class LocationPayload:
    def __init__(self, j):
        self.__dict__ = json.loads(j)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("sani/location")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payloadStr = msg.payload.decode('ASCII')
    payload = LocationPayload(payloadStr)
    try:
        conn = psycopg2.connect("dbname='ta_sani' user='sani_ta' host='45.127.134.18' password='1234567890'")
        # conn = psycopg2.connect("dbname='ta_sani' user='sani_ta'")
        cur = conn.cursor()
        execSql = "UPDATE DRIVER SET LATITUDE={driver.latitude}, LONGITUDE={driver.longitude}," \
                  "LAST_MODIFIED='{current}' " \
                  "WHERE DRIVER_UUID='{driver.driver_uuid}';".format(driver=payload, current=datetime.datetime.utcnow())
        print(execSql)
        cur.execute(execSql)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    print(payload)
    # print(msg.topic + " " + str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("45.127.134.18", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
