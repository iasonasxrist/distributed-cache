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

class CacheGateway:
    def __init__(self) -> None:
        self.zkClient = zookeeperClient(hosts = ZOOKEEPER_HOST)

    def start(self):
        logging.info(f"Starting cache node with HOSTNAME {HOSTNAME}")
        #Node is eligible to be leader of follower according to the sequence number of znode
        self.zkClient.registerCacheNode()
        self.zkClient.dumpCacheNodeStatus()
        #Init HTTP server
        app.run(host='0.0.0.0', port=5000)
        logging.info("Server is up and running")


cacheGateway = CacheGateway()


@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        # round-robin
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
        
        cached_data = cacheNode.retrieve(key)
        logging.info(f'Retrieved data for key: {key}')
        return jsonify(cached_data)
        
    elif request.method == 'POST':
        
        key = request.args.get('key')
        value = request.args.get('value')
        
        if not (key and value):
            logging.error('No data given.')
            return 'No data given.', 422

        if cacheGateway.amICacheLeader():
            try:
                cacheGateway.insert(key, value)
            except:
                return 'Failed to insert data', 501
        
        else:
            leader_hostname = cacheGateway.getHostNameOfCacheLeader()
            return redirect(f'http://{leader_hostname}:5000/data?key={key}&value={value}')
        
    else:
        return 'Internal Server Error.', 501

    
if __name__ == '__main__':
    cacheGateway.start()