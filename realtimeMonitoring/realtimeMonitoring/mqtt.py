from datetime import datetime
import json
import paho.mqtt.client as mqtt
from django.conf import settings
from . import utils

def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    
    try:
        time = datetime.now()
        payload = message.payload.decode("utf-8")
        print("payload: " + payload)
        payloadJson = json.loads(payload)
        country, state, city, user = utils.get_topic_data(message.topic)
        user_obj = utils.get_user(user)
        location_obj = utils.get_or_create_location(city, state, country)
        for measure in payloadJson:
            variable = measure
            unit = utils.get_units(str(variable).lower())
            variable_obj = utils.get_or_create_measurement(variable, unit)
            sensor_obj = utils.get_or_create_station(user_obj, location_obj)
            utils.create_data(float(payloadJson[measure]), sensor_obj, variable_obj, time)
    except Exception as e:
        print('Ocurrió un error procesando el paquete MQTT', e)

def on_disconnect(client: mqtt.Client, userdata, rc):
    '''
    Función que se ejecuta cuando se desconecta del broker.
    Intenta reconectar al bróker.
    '''
    print("Desconectado con mensaje:" + str(mqtt.connack_string(rc)))
    print("Reconectando...")
    client.reconnect()

def start_mqtt():
    '''
    Inicia el cliente MQTT y se conecta al broker.
    '''
    client = mqtt.Client()
    client.on