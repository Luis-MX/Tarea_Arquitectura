#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_acelerometro.py
# Capitulo: 4 Estilo Publica-Subscribe
# Autor(es): Raúl Bermúdez, Luis Alcalá, Luis Ortiz & Jorge Solís
# Version: 1.0 Marzo 2019
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                  procesador_de_acelerometro.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar valores     |    por el wearable     |
#           |     Procesador del    |    extremos de las      |    Xiaomi My Band.     |
#           |     Acelerómetro      |    posiciones para      |  - Define el rango de  |
#           |                       |    detectar una caída.  |    valores extremos    |
#           |                       |                         |    para las posiciones |
#           |                       |                         |    en los ejes X, Y    |
#           |                       |                         |    y Z.                |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    cuando los valores  |
#           |                       |                         |    extremos son detec- |
#           |                       |                         |    tados.              |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe las posi-   |
#           |       consume()        |          Ninguno         |    ciones de los ejes |
#           |                        |                          |    desde el distribui-|
#           |                        |                          |    dor de mensajes.   |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores extremos   |
#           |                        |     Rabbit.              |    de las posiciones  |
#           |       callback()       |  - properties: propio de |    de los ejes X, Y   |
#           |                        |     Rabbit.              |    y Z.               |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepción de datos, para éste ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time
import logging


class ProcesadorAcelerometro:

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviará la posición
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='accelerometer', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(self.callback, queue='accelerometer')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        if float(json_message['x_position']) <= 0.4 and float(json_message['y_position']) >= 0.6 and float(json_message['z_position']) <= 0.4:
            monitor = Monitor()
            monitor.print_notification(json_message['datetime'], json_message['id'], json_message[
                                       'x_position'], 'aceleración', json_message['model'], y_position=json_message['y_position'], z_position=json_message['z_position'])
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def string_to_json(self, string):
        message = {}
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_acelerometro = ProcesadorAcelerometro()
    p_acelerometro.consume()
