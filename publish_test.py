#! /usr/bin/python3

import pika
from rmq_params import rmq_params
import pickle
import time

def send_message(headline, timestamp):
    to_send = pickle.dumps((headline,timestamp))
    channel.basic_publish(exchange=rmq_params["exchange"], routing_key="r_key", 
                                body=to_send)


if __name__ == "__main__":
    #setup rabbitmq stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters(virtual_host=rmq_params["vhost"], 
                                                credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    time.sleep(2)
    send_message("test 0", int(time.time()))
    time.sleep(1)
    send_message("test 1", int(time.time())-1800)
    time.sleep(1)
    send_message("test 2", int(time.time())-4000)
    time.sleep(1)
    send_message("test 3", int(time.time()))

    connection.close()
