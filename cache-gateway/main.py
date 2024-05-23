from flask import Flask, jsonify, request, redirect
from zookeeper.zookeeperClient import zookeeperClient
from cache.cache import LRUCache
import logging
import os
import requests
import atexit



app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# HOST is provided by docker and refers to the hostname of the container
HOSTNAME = os.getenv('HOSTNAME', 'localhost') 
REGISTRATION_ZK_PATH = '/registeredCacheNodes'
ZOOKEEPER_HOST = os.getenv('ZOOKEEPER_HOST', 'zookeeper:2181') 
MAX_SIZE = 30

class CacheHTTPNode:
    def __init__(self) -> None:
        self.zkClient = zookeeperClient(hosts = ZOOKEEPER_HOST)
        self.cache = LRUCache(MAX_SIZE)

    def start(self):
        logging.info(f"Starting cache node with HOSTNAME {HOSTNAME}")
        #Node is eligible to be leader of follower according to the sequence number of znode
        self.registerCacheNode()
        self.dumpCacheNodeStatus()
        #Init HTTP server
        app.run(host='0.0.0.0', port=5000)
        logging.info("Server is up and running")