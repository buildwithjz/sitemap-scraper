import pymongo
import json
import csv
import time
import os

SITEMAP_FOLDER = "./"

def query_db(collection, topic):

    existing_links = []

    query = { "topic": topic}

    #Is a pymongo cursor object
    all_topic_links = collection.find(query)

    for topic_link in all_topic_links:
        existing_links.append(topic_link["url"])

    return existing_links


# Pass in the results from query db and the results of the sitemaps by domain
def get_new_links(topic, search_domain, stripped_domain, existing_links):

    links_to_add = []

    with open(SITEMAP_FOLDER + '/' + stripped_domain+".json", 'r') as fin:
        domain_links = json.load(fin)
        for domain_link in domain_links:
            if process_entry(domain_link, search_domain):

                #This is currently all links that match
                #print(domain_link)

                if domain_link['url'] not in existing_links:
                    links_to_add.append(build_entry(domain_link, topic))

    return links_to_add

def process_entry(domain_link, search_domain):
    # Assume all are new additions
    if search_domain in domain_link['url']:
        return True

def build_entry(domain_link, topic):
    final_entry = {
        "url": domain_link['url'],
        "domain": domain_link['domain'],
        "topic": topic,
        "reads": 0,
        "recommends": 0
    }
    return final_entry

def write_topic_to_db(topic, search_domain, stripped_domain):
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_USER_PASS']
    DB_NAME = os.environ['DB_NAME']
    DB_ENDPOINT = os.environ['DB_ENDPOINT']
    
    client = pymongo.MongoClient("mongodb://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_ENDPOINT, DB_NAME))
    db = client.saga

    collection = db.links

    existing_links = query_db(collection, topic)

    links_to_add = get_new_links(topic, search_domain, stripped_domain, existing_links)
    
    if (len(links_to_add) > 0):
        x = collection.insert_many(links_to_add)
    