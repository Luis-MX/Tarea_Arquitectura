#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: monitor.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz.
# Version: 2.0.1 Mayo 2017
# Descripción:
#
#   Ésta clase define el rol del monitor, es decir, muestra datos, alertas y advertencias sobre los signos vitales de los adultos mayores.
#
#   Las características de ésta clase son las siguientes:
#
#                                            monitor.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |        Monitor        |  - Mostrar datos a los  |         Ninguna        |
#           |                       |    usuarios finales.    |                        |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |  print_notification()  |  - datetime: fecha en que|  - Imprime el mensa-  |
#           |                        |     se envió el mensaje. |    je recibido.       |
#           |                        |  - id: identificador del |                       |
#           |                        |     dispositivo que      |                       |
#           |                        |     envió el mensaje.    |                       |
#           |                        |  - value: valor extremo  |                       |
#           |                        |     que se desea notifi- |                       |
#           |                        |     car.                 |                       |
#           |                        |  - name_param: signo vi- |                       |
#           |                        |     tal que se desea no- |                       |
#           +------------------------+--------------------------+-----------------------+
#           |   format_datetime()    |  - datetime: fecha que se|  - Formatea la fecha  |
#           |                        |     formateará.          |    en que se recibió  |
#           |                        |                          |    el mensaje.        |
#           +------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------


class Monitor:

    #Se realizaron modificaciones para poder utilizar este método
    # para mostrar los mensajes de los distintos procesadores.
    def print_notification(self, datetime, id, value, name_param, model, y_position=None, z_position=None, dosis=None):
        print "  ---------------------------------------------------"
        print "    ADVERTENCIA"
        print "  ---------------------------------------------------"
        if y_position is not None:
            print "    Posible caida. Se ha detectado un incremento de " + str(name_param) + " (" + str(value) + ", " \
                  + str(y_position) + ", " + str(z_position) + ")" + " a las " + str(
                self.format_datetime(datetime)) + " en el adulto mayor que utiliza el dispositivo " + str(
                model) + ":" + str(id)
            print ""
        elif dosis is not None:
            print "    El adulto mayor con id " + str(
                id) + " debe tomar la dosis " + dosis + " del medicamento " + value + " a las " + str(
                self.format_datetime(datetime))+ "."
            print ""
        else:
            print "    Se ha detectado un incremento de " + str(name_param) + " (" + str(value) + ")" + " a las " + \
                  str(self.format_datetime(datetime)) + " en el adulto mayor que utiliza el dispositivo " + str(model) + ":" + str(id)

    def format_datetime(self, datetime):
        values_datetime = datetime.split(':')
        f_datetime = values_datetime[3] + ":" + values_datetime[4] + " del " + \
            values_datetime[0] + "/" + \
            values_datetime[1] + "/" + values_datetime[2]
        return f_datetime
