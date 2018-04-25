#! /usr/bin/python3

import pika
import time
from rmq_params import rmq_params
import sys
import pickle

import curses
import time
import threading

headline_list = []
list_lock = threading.RLock()

frametime = 0.1
display_len = 50
separator = " ||| "

def time_is_good(timestamp):
	#time_cutoff = current time - 1 hour (in seconds)
	time_cutoff = int(time.time()) - 3600
	if timestamp > time_cutoff:
		return True
	else:
		return False

#pops the next item to print in the scrolling display
#	from the front of headline_list, ensures the timestamp
#	is within the display window (discarding the item and 
#	choosing another if not), then appends the popped item 
#	to the back of headline_list, and returns a copy of it.
#
#if the list is empty (or becomes empty as timed-out headlines
#	are discarded), this function returns an empty string
def get_next_item():
	global headline_list
	list_lock.acquire()

	item = ""
	if headline_list:
		(headline, timestamp) = headline_list.pop(0)
		if(time_is_good(timestamp)):
			headline_list.append((headline, timestamp))
		else:
			item = get_next_item()

	list_lock.release()
	return headline

#main function of the display thread
def display3(stdscr):
	global frametime, display_len, separator
	stdscr = curses.initscr()
	curses.noecho()

	to_display = ""
	save_idx = 0
	while True:
		while len(to_display) < display_len:
			if(save_idx == 0):
				item = get_next_item() + separator
			for i in range(save_idx, len(item)):
				to_display += item[i]
				if len(to_display) == display_len:
					if(i+1 == len(item)):
						save_idx = 0
					else:
						save_idx = i+1
					break
		temp = to_display[1:]
		stdscr.addstr(0,0, to_display)
		to_display = temp
		stdscr.refresh()
		time.sleep(frametime)
		
def client_callback(ch, method, properties, body):
	#data should be tuple (headline, timestamp)
	item = pickle.loads(body)
	list_lock.acquire()
	headline_list.append(item)
	list_lock.release()

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

        print("nonsense")
        #spawn display thread:
        curses.wrapper(display3)


