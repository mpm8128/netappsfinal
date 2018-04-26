#!/usr/bin/python3

import curses
import time
import threading

headline_list = []
#sample_list = ["item 1", "item 2", "item 3", "item 4"]

list_lock = threading.RLock()

max_x = 0
max_y = 0

frametime = 0.1
display_len = 50
separator = " ||| "
cutoff = 30

def time_is_good(timestamp):
	global cutoff
	#time_cutoff = current time - 1 hour (in seconds)
	time_cutoff = int(time.time()) - cutoff
	if timestamp > time_cutoff:
		return True
	else:
		return False

def get_next_item():
	global headline_list
	list_lock.acquire()

	item = ""
	if headline_list:
		(headline, timestamp) = headline_list.pop(0)
		item = headline + ";; " + str(timestamp % 3600)
		#item = headline
		if(time_is_good(timestamp)):
			headline_list.append((headline, timestamp))
		else:
			print("\n" + headline + " " + str(timestamp) + " timed out at: " + str(time.time()))
			item = get_next_item()

	list_lock.release()
	return item

def display3(stdscr):
	global frametime, display_len, separator, max_y, max_x
	stdscr = curses.initscr()
	curses.noecho()

	to_display = ""
	save_idx = 0
	framecount = 0
	q = 0
	while True:
		(max_y, max_x) = stdscr.getmaxyx()
		display_len = max_x - 2
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
		stdscr.addstr(0,1, to_display)
		temp = to_display[1:]
		to_display = temp
		stdscr.refresh()
		time.sleep(frametime)
		framecount += 1
		if (framecount % 30 == 0) and q < 10:
			list_lock.acquire()
			headline_list.append( (("item " + str(q)), int(time.time())) )
			list_lock.release()
			q += 1
		

curses.wrapper(display3)
