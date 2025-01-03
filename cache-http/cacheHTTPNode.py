from flask import Flask, jsonify, request, redirect
from zookeeper.zookeeperClient import zookeeperClient
from cache.cache import LRUCache
import logging
import os
import requests


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
        #Node is eligible to be leader or follower according to the sequence number of znode
        self.zkClient.registerCacheNode(REGISTRATION_ZK_PATH, HOSTNAME)
        self.zkClient.dumpCacheNodeStatus(REGISTRATION_ZK_PATH)
        app.run(host='0.0.0.0', port=5000)
        logging.info("Server is up and running")
            
    def amICacheLeader(self) -> bool:
        return self.zkClient.getHostNameOfCacheLeader(REGISTRATION_ZK_PATH) == HOSTNAME

    def insert(self, key, value):

        self.cache.set(key, value)
        if cacheNode.amICacheLeader():
            
            followers = self.zkClient.getHostNameOfCacheFollowers(REGISTRATION_ZK_PATH)
            logging.info(f" **Replicate data to followers**")
            for follower, hostname in enumerate(followers):
                    response = requests.post(f'http://{hostname}:5000/data?key={key}&value={value}')
                    response.raise_for_status()
 
    def retrieve(self, key):

        cached_data = self.cache.get(key)
        if cached_data is not None:
            return cached_data
        return {}
    
cacheNode = CacheHTTPNode()    

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
        
        cached_data = cacheNode.retrieve(key)
        if cached_data is None:
            logging.error(f'No data found for key: {key}')
            return 'No data found for the given key.', 404
        logging.info(f'Retrieved data for key: {key}')
        return jsonify(cached_data)
        
    elif request.method == 'POST':
        key = request.args.get('key')
        value = request.args.get('value')
        
        if not (key and value):
            logging.error('No data given.')
            return 'No data given.', 422
       
        try:
            cacheNode.insert(key, value)
            logging.info(f'Data inserted for key: {key}')
            return 'Data inserted successfully.', 201
        except Exception as e:
            logging.error(f'Failed to insert data: {e}')

    return 'Internal Server Error.', 500
if __name__ == '__main__':
    cacheNode.start()

