import os
import pymongo

def get_next_topic(collection):

    query = {"currently_updating": {'$ne': True}}
    topics = list(collection.find(query))
    for topic in topics:
        if 'last_updated' not in topic.keys():
            topic_name = topic['topic']
            set_flag(collection, topic_name)
            return topic['topic'], topic['filtered-url']
    sorted_topics = sorted(topics, key=lambda k: k['last_updated'])
    topic = sorted_topics[0]
    topic_name = topic['topic']
    return topic['topic'], topic['filtered-url']

def set_flag(collection, topic):
    query = {"topic": topic}
    flag = {"$set": {"currently_updating": True}}
    collection.update_one(query, flag)

def reset_flag_for_all(collection):
    flag = {"$set": {"currently_updating": False}}
    collection.update_many({}, flag)
    exit(0)
