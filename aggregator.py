#! /usr/bin/python3

import sqlite3
import feedparser
import time
import pika
from rmq_params import rmq_params
import pickle

check_rate = 60 # Time (in seconds) between checks

def send_message(headline, timestamp, topic):
    global connection
    try:
        print("Sending '%s' to %s" % (headline, topic))
        to_send = pickle.dumps((headline,timestamp))
        channel.basic_publish(exchange=rmq_params["exchange"], routing_key=topic, body=to_send)
    except Exception as e:
        print(e)
        
def publish_headlines(new_headlines, topic):
    timestamp = time.time()
    for headline in new_headlines:
        send_message(headline, timestamp, topic)

def save_headline(headline, conn):
    # Checking to see if the headline is already in the database
    cur = conn.cursor()
    check_sql = 'SELECT * FROM headlines WHERE headline=?'
    cur.execute(check_sql, [headline])
    if cur.fetchone() is not None:
        return False
    
    # Inserting the headline into the database
    cur = conn.cursor()
    sql = 'INSERT INTO headlines(headline) VALUES(?)'
    try:
        cur.execute(sql, [headline])
    except Exception as e:
        print(e)
        return False
    return True

def get_new_headlines():
    conn = sqlite3.connect('feeds.db')
    
    headlines = {}
    
    # Iterate through feeds in the database
    print("Parsing news feeds")
    for row in conn.execute("SELECT * FROM feeds ORDER BY category"):
        feed_name = row[1]
        feed_url = row[2]
        category = row[3]
        curr_headlines = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed["entries"]:
                headline = entry["title"]
                if len(headline) > 0 and save_headline("%s - %s" % (headline, feed_name), conn):
                    print("New headline: %s" % headline)
                    curr_headlines.append({"title" : headline, "source" : feed_name})
            if category in headlines:
                headlines[category].extend(curr_headlines)
            else:
                headlines[category] = curr_headlines
        except Exception as e:
            print(e)
       
    # Saving changes and closing sqlite connection
    conn.commit()
    conn.close()
            
    print("Parsed")
    
    return headlines
        
if __name__ == "__main__":
    # Set Up RabbitMQ stuff
    credentials = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
    parameters = pika.ConnectionParameters('172.29.63.121', 5672, virtual_host=rmq_params["vhost"], credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Checking loop
    while True:
        all_headlines = get_new_headlines()
        for category in all_headlines:
            curr_headlines = [headline["title"] for headline in all_headlines[category]]
            publish_headlines(curr_headlines, category)
        time.sleep(check_rate)