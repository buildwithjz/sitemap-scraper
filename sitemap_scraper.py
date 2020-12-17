from generate_sitemap import *
from write_topic_to_db import *
from get_next_topic import *
import pymongo
import argparse
import logging
import time
import datetime
import os

def get_existing_sitemaps():
  sitemaps = []
  for f in listdir(SITEMAP_FOLDER):
    sitemaps.append(f.split('.json')[0])
  return sitemaps

# python3 sitemap_scraper.py <topic> <domain>
# python3 sitemap_scraper.py docker https://docs.docker.com
'''
def main():
    domains_generated = ['']

    # TODO: Condition to see if the --all flag is NOT SET
    if True:
        domains_generated = get_existing_sitemaps()

    # Will not generate duplicate sitemaps
    topic = sys.argv[1]
    search_domain = sys.argv[2]
    stripped_domain = strip_domain(search_domain)

    print("Reading topic: ",topic,", \tdomain: ", search_domain, "\tstripped domain: ", stripped_domain)
    if stripped_domain not in domains_generated:
        generate_sitemap(search_domain)
            
    write_topic_to_db(topic, search_domain, stripped_domain)
'''

def graceful_exit(collection, topic):
    collection = db.topics

    query = {"topic": topic}
    flag = {"$set": {"currently_updating": False}}
    collection.update(query, flag)

    exit(0)

def successful_exit(collection, topic):
    query = {"topic": topic}
    flag = {"$set": {"currently_updating": False}}
    last_updated = {"$set": {"last_updated": datetime.datetime.utcnow()}}
    collection.update_one(query, flag)
    collection.update_one(query, last_updated)
    
    final_row = collection.find(query)
    return final_row[0]

def build_db_topic_connection():
    
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_USER_PASS']
    DB_NAME = os.environ['DB_NAME']
    DB_ENDPOINT = os.environ['DB_ENDPOINT']
    
    client = pymongo.MongoClient("mongodb://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_ENDPOINT, DB_NAME))
    db = client.saga

    collection = db.topics

    return collection


def main():
    # Format the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="The topic to generate a sitemap for")
    parser.add_argument("--domain", help="The search domain for links")
    parser.add_argument("--reset", help="Ignores all other inputs and resets the currently updating flag for all topics")
    args = parser.parse_args()

    # Configure logging
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',level=logging.DEBUG)
    logging.info("Started sitemap scraper for saga")

    topic = ""
    search_domain = ""

    try:
        collection = build_db_topic_connection()
    except Exception as e:
        logging.error("Could not connect to the database")
        logging.error(e)
        exit(0)

    if (args.reset):
        logging.info("--reset flag has been set. Resetting current_updating flag and exiting")
        reset_flag_for_all(collection)

    if (args.topic or args.domain):
        if not (args.domain and args.topic):
            logging.warning("Both --topic and --domain must be set")
            logging.warning("Exiting: 0")
            exit(0)
        else:
            topic = args.topic
            search_domain = args.domain
            set_flag(collection, topic)
    else:
        logging.info("No arguments provided, searching for next available topic")
        try:
            topic, search_domain = get_next_topic(collection)
            set_flag(collection, topic)
        except Exception as e:
            logging.warning(e)
            logging.warning("Error getting latest topic to scrape from db")
            exit(0)

    try:
        stripped_domain = strip_domain(search_domain)
    except:
        logging.warning("Can't strip domain properly - ensure that domain is in format http://<domain>[/...]")
        logging.warning("Exiting: 0")
        exit(0)

    logging.info("Scraping for topic: '{}'".format(topic))
    logging.info("Under search domain '{}'".format(search_domain))
    logging.info("For the domain: '{}'".format(stripped_domain))

    try:
        logging.info("========== STARTING SCRAPE ==========")
        generate_sitemap(search_domain)
        logging.info("========== FINISHED SCRAPE ==========")
    except Exception as e:
        logging.error(e)
        logging.error("Can't generate sitemap links")
        logging.error("Exiting: 0")
        graceful_exit(collection, topic)

    try:
        logging.info("Writing topic links to mongodb")
        write_topic_to_db(topic, search_domain, stripped_domain)
        logging.info("Final object: ")
        logging.info(successful_exit(collection, topic))
        logging.info("All jobs successfuly, exiting: 0")
        exit(0)
    except Exception as e:
        logging.error(e)
        logging.error("Can't write topics to db")
        logging.error("Exiting: 0")
        graceful_exit(collection, topic)

if __name__ == "__main__":
    main()