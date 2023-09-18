import schedule
import time
from datetime import datetime, timedelta
from django.db.models import Avg
from receiver.models import Measurement
from mqtt import client, publish_alert_message
from django.db.models import Avg


def start_cron():
    """
    Inicia el cron que se encarga de ejecutar la función analyze_data cada minuto.
    """
    print("Iniciando cron...")
    schedule.every(1).minutes.do(analyze_data)
    print("Servicio de control iniciado")

    while True:
        schedule.run_pending()
        time.sleep(1)

def analyze_data():
    """
    Realiza los cálculos necesarios para identificar si hay que enviar mensajes de alerta a los dispositivos.
    """
    print("Calculando alertas...")
    data = Measurement.objects.filter(timestamp__gte=datetime.now() - timedelta(hours=1))
    aggregation = data.values('user').annotate(average_temperature=Avg('temperature'))

    alerts = 0
    for item in aggregation:
        user = item['user']
        average_temperature = item['average_temperature']

        # Obtener los límites de temperatura para el usuario
        min_temperature = user.temperature_limit_min
        max_temperature = user.temperature_limit_max

        # Verificar si el promedio de temperatura está fuera de los límites
        if average_temperature < min_temperature or average_temperature > max_temperature:
            # Enviar mensaje de alerta al dispositivo
            publish_alert_message(user, average_temperature, min_temperature, max_temperature)
            alerts += 1

    print(f"Se revisaron {len(aggregation)} dispositivos")
    print(f"Se enviaron {alerts} alertas")


def get_average_temperature():
    # Consultar la base de datos para obtener la temperatura promedio
    average_temperature = Measurement.objects.aggregate(Avg('temperature'))['temperature__avg']
    return average_temperature

def analyze_data():
    # Obtener el valor promedio de la temperatura
    average_temperature = get_average_temperature()

    # Evaluar la condición del evento
    if average_temperature > x:
        # Ejecutar la acción del evento
        # Por ejemplo, encender un LED
        led.on()

start_cron()