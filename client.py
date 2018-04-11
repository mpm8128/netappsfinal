#! /usr/bin/python3

import pika
import time
from rmq_params import rmq_params
import sys
import pickle

def user_display(headline):
    #placeholder function
    print(str(headline))

def client_callback(ch, method, properties, body):
    #data should be tuple (headline, timestamp)
    (headline, timestamp) = pickle.loads(body)

    #maintain list of headlines
    #prune old headlines
    #display "recent" headlines
    #	might want to do these things in another thread
    
    #time_cutoff = current time - 1 hour (in seconds)
    time_cutoff = int(time.time()) - 3600
    if timestamp > time_cutoff:
        user_display(headline)
    #else discard it

if __name__ == "__main__":
    #setup rabbitmq stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters(virtual_host=rmq_params["vhost"], 
                                                credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
	
    binding_keys = sys.argv[1:]
    if not binding_keys:
        #usage statement
        sys.exit(1)
	
    for binding_key in binding_keys:
        channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name,
                            routing_key=binding_key)

        channel.basic_consume(client_callback, queue=queue_name, no_ack=True)
        channel.start_consuming()
