#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_tiempo.py
# Capitulo: 4 Estilo Publica-Subscribe
# Autor(es): Raúl Bermúdez, Luis Alcalá, Luis Ortiz & Jorge Solís
# Version: 1.0 Marzo 2019
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                  procesador_de_tiempo.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar la hora     |    por el wearable     |
#           |     Procesador de     |    actual que permita   |    Xiaomi My Band.     |
#           |     Tiempo            |    emitir un recorda-   |  - Evalúa la hora      |
#           |                       |    torio para la toma   |    actual para emitir  |
#           |                       |    de medicamentos.     |    la notificación de  |
#           |                       |                         |    toma de medicamen-  |
#           |                       |                         |    tos.                |
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
#           |                        |  - ch: propio de Rabbit. |  - Procesa le hora    |
#           |                        |  - method: propio de     |    actual para el     |
#           |                        |     Rabbit.              |    envío de notifi-   |
#           |       callback()       |  - properties: propio de |    caciones.          |
#           |                        |     Rabbit.              |                       |
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
import random


class ProcesadorTiempo:

    def __init__(self):
        self.tablaMedicamentos = {}
        self.contador = 0
        self.idImpreso = []

        self.medicamentos = {
            'Ibuprofeno': (),
            'Paracetamol':(),
            'Insulina':(),
            'Furosemida':(),
            'Piroxicam':(),
            'Tolbutamida':()
        }

        '''
        self.medicamentos = (
            'Ibuprofeno',
            'Paracetamol',
            'Insulina',
            'Furosemida',
            'Piroxicam',
            'Tolbutamida'
        )'''


    def consume(self):
        try:
            logging.basicConfig()
            # Url que define la ubicación del Distribuidor de Mensajes
            url = 'amqp://oevvxuqp:D6vn6A9ErigVUrxOINL-ok-vdD610S_I@wombat.rmq.cloudamqp.com/oevvxuqp'
            # Se utiliza como parámetro la URL dónde se encuentra el Distribuidor
            # de Mensajes
            params = pika.URLParameters(url)
            params.socket_timeout = 5
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(params)
            # Se solicita un canal por el cuál se enviará la fecha y hora actual.
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='datetime', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(self.callback, queue='datetime')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)

        if self.tablaMedicamentos.items().__len__() == 0:
            hora_base = self.obtenerHoraBase(json_message['datetime'])
            self.asignarHoraMedicamento(hora_base)

        if not json_message['id'] in self.tablaMedicamentos:
            self.asignarMedicamento(json_message['id'], json_message['datetime'])

        #print self.tablaMedicamentos

        if self.esHoraDeMedicamento(json_message['datetime'],
                                    self.tablaMedicamentos[json_message['id']]['medicamento'][1]):
            if(json_message['id'] not in self.idImpreso):
                monitor = Monitor()
                monitor.print_notification(json_message['datetime'], json_message['id'], self.tablaMedicamentos[
                        json_message['id']]['medicamento'][0],
                        json_message['model'],'',
                        dosis=self.tablaMedicamentos[json_message['id']]['dosis'])
                self.idImpreso.append(json_message['id'])
        #print self.contador
        #self.contador += 1


        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def asignarHoraMedicamento(self, hora):
        count = 0
        for clave in self.medicamentos:
            self.medicamentos[clave]=hora
            if count%2 == 1:
                hora = self.incrementarHora(hora)
            count += 1
            #print self.medicamentos[clave]


    def asignarMedicamento(self, id, hora_base):
        clave = random.choice(self.medicamentos.keys())
        registro =  {
            'medicamento': (clave, self.medicamentos[clave]),
            #'hora_base': self.obtenerHoraBase(hora_base),
            'intervalo': 60,
            #'medicamento': self.medicamentos[random.randint(0, len(self.medicamentos)-1)],
            'dosis': '50mg'
        }
        #print registro['medicamento']
        self.tablaMedicamentos[id] = registro

    def esHoraDeMedicamento(self, strtime, hora_base):
        values_datetime = strtime.split(':')
        hora = int(values_datetime[3]), int(values_datetime[4]), int(values_datetime[5])
        esHora= False
        #if hora[0] == hora_base[0] and hora[1] == hora_base[1] and abs(hora[2] - hora_base[2]) < 31:
        if hora[0] == hora_base[0] and abs(hora[1] - hora_base[1]) < 2:
        #if hora[0] == hora_base[0] and hora[1] == hora_base[1]:
            esHora = True
        return esHora

    def string_to_json(self, string):
        message = {}
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

    def obtenerHoraBase(self, datetime):
        values_datetime = datetime.split(':')
        if int(values_datetime[5]) + 30 > 59:
            values_datetime[5] = int(values_datetime[5]) - 30
            values_datetime[4] = int(values_datetime[4]) + 1
            if values_datetime[4] > 59:
                values_datetime[4] = 0
                if int(values_datetime[3]) == 23:
                    values_datetime[3] = 0
        else:
            values_datetime[5] = int(values_datetime[5]) + 30
        datetime = int(values_datetime[3]), int(values_datetime[4]), values_datetime[5]
        return datetime

    def incrementarHora(self, horaCompleta):
        hora = None
        if int(horaCompleta[0]) == 23:
            hora = 0
        else:
            hora = horaCompleta[0] + 1
        datetime = int(hora), int(horaCompleta[1]), int(horaCompleta[2])

        return datetime


if __name__ == '__main__':
    p_tiempo = ProcesadorTiempo()
    p_tiempo.consume()
