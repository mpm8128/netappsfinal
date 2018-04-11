#! /usr/bin/python3

import pika
from rmq_params import rmq_params
import pickle

def debug_callback(ch, method, properties, body):
    data = pickle.loads(body)	#data should be tuple containing (headline, timestamp)
    #print("Headline: " + str(data[0]))
    #print("Timestamp: " + str(data[1]))
	

if __name__ == "__main__":
    #setup rabbitmq stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters(virtual_host=rmq_params["vhost"], 
                                            credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(rmq_params["exchange"], exchange_type='topic')

    channel.queue_declare("debug_queue", auto_delete=True)
    channel.queue_bind(exchange=rmq_params["exchange"], queue="debug_queue", 
                        routing_key="#")

    channel.basic_consume(debug_callback, queue="debug_queue", no_ack=True)
    channel.start_consuming()
