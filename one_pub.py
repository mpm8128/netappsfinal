#! /usr/bin/python3

import pika
from rmq_params import rmq_params
import pickle
import time
import sys

server_ip = '172.29.51.245'
server_port = 5672


def send_message(headline, timestamp, r_key):
    to_send = pickle.dumps((headline,timestamp))
    channel.basic_publish(exchange=rmq_params["exchange"], routing_key=r_key, 
                                body=to_send)


if __name__ == "__main__":
    #setup rabbitmq stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters(server_ip, server_port, virtual_host=rmq_params["vhost"], 
                                                credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    time.sleep(2)
    send_message(sys.argv[1], int(time.time()), sys.argv[2])

    connection.close()
