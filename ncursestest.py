#!/usr/bin/python3

import curses
import time
import threading

sample_text = "Attributes allow displaying text in highlighted forms. "
#sample_list = []
sample_list = ["item 1", "item 2", "item 3", "item 4"]

list_lock = threading.RLock()

frametime = 0.1
display_len = 50
separator = " ||| "

def get_next_item():
	global sample_list
	list_lock.acquire()

	item = ""
	#take the next item from the front of the list, and add it to the back
	if sample_list:
		item = sample_list.pop(0)
		sample_list.append(item)

	list_lock.release()
	return item

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

curses.wrapper(display3)
