#! /usr/bin/python3

import pika
from rmq_params import rmq_params
import pickle
import time

def send_message(headline, timestamp, topic):
    to_send = pickle.dumps((headline,timestamp))
    channel.basic_publish(exchange=rmq_params["exchange"], routing_key=topic,
                                body=to_send)

def publish_headlines(new_headlines, topic):
    timestamp = time.time()
    for headline in new_headlines:
        #timestamp = headline["timestamp"]
        send_message(headline, timestamp, topic)

if __name__ == "__main__":
    #parse configuration/arguments
    #   file(s) to read topics/feeds from?
    #   host/address and port of message broker

    #setup rabbitmq stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters(virtual_host=rmq_params["vhost"], 
                                                credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    last_time = time.time()

    #periodically check RSS feeds
    #while(True)
    #   for topic in topics:
    #       new_headlines = []
    #       #check RSS feeds
    #       for feed in rss_feeds:
    #           #get/parse data
    #           #if timestamp > last_time:
    #               new_headlines.append(feed_data)
    #       #end for
    #       #if new_headlines != []:
    #           publish_headlines(new_headlines, topic)
    #   #end for
    #
    #   #update our idea of what is recent
    #   last_time = time.time()
    #
    #   time.sleep(60*1) #sleep 1 minute
    #end while

    #send_message("test 0", int(time.time()), "politics")

    connection.close()
