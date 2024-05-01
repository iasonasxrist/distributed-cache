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

    def registerCacheNode(self):
        return self.zkClient.registerSequentialZNode(path = REGISTRATION_ZK_PATH+  '/node_', data = HOSTNAME)
        
    def getHostNameOfCacheLeader(self):
        return self.zkClient.getZNodeData(
            REGISTRATION_ZK_PATH + "/" + self.zkClient.getSortedSubNodes(path = REGISTRATION_ZK_PATH)[0]
        )

    def getHostNameOfCacheFollowers(self):
        followerPaths = self.zkClient.getSortedSubNodes(path = REGISTRATION_ZK_PATH)
        #Remove first subNode since it is leader  
        if len(followerPaths) > 1:
            followerPaths = followerPaths[1:]
        followersList = [self.zkClient.getZNodeData(REGISTRATION_ZK_PATH + "/" + followerPath) for followerPath in followerPaths]
        return followersList
    
    def dumpCacheNodeStatus(self):
        logging.info(f"Leader is {self.getHostNameOfCacheLeader()}")

        followers =  self.getHostNameOfCacheFollowers()
        for index, followerHostName in enumerate (followers):
            logging.info(f"Follower {index} with hostname {followerHostName}")
            
    def amICacheLeader(self) -> bool:
        return self.getHostNameOfCacheLeader() == HOSTNAME;

    
    
    def insert(self, key, value):
        if self.amICacheLeader():
            
            # I am the leader
            # Update local cache
            self.cache.set(key, value)

            # Replicate data to followers
            followers = self.getHostNameOfCacheFollowers()
            if followers is None:
                logging.info("No nodes were found to send data.")
                return None
            
            toSend = {key: value}

            for follower, hostname in enumerate(followers):
                try:
                    response = requests.post(f'http://{hostname}:5000/data?key={key}&value={value}')
                    response.raise_for_status()  # Raise an exception for HTTP errors
                except Exception as e:
                    logging.error(f"Error occurred while replicating data to node {follower}: {e}")
        else:

            self.redirectToLeader(key, value)
         
    def redirectToLeader(self, key, value):

        logging.info("*Forwarding Reques to Leader*")
        leader_address = self.getHostNameOfCacheLeader()
        logging.info(f"Leader Address: {leader_address}")

        url = f'http://{leader_address}:5000/leader_redirection?key={key}&value={value}'
        

        return redirect(url, code = 302)
            

    def retrieve(self, key):

        cached_data = self.cache.get(key)

        if cached_data is not None:
            return cached_data


        if self.amICacheLeader():
            logging.info(f"Data not found locally for key: {key}, and I am the leader")
            return  {"error": "Data not found"}
            
    
cacheNode= CacheHTTPNode()    

@app.route("/leader_redirection")
def handle_redirection():
        
    key = request.args.get('key')
    value = request.args.get('value')
    
    if not (key and value):
        logging.error('No data given.')
        return 'No data given.', 422

    inserted_data = cacheNode.insert(key, value)

    logging.info(f'Data inserted for key: {key}')
    logging.info(f"Successfully forwarded request to leader")
    return 'Data inserted successfully.', 201



@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
        
        cached_data = cacheNode.retrieve(key)
        logging.info(f'Retrieved data for key: {key}')
        return jsonify(cached_data)
        
        # leader_address = self.getHostNameOfCacheLeader()

        # url = f"http://{leader_address}/data?key={key}"
        # try:
        #     response = requests.get(url)
        #     response.raise_for_status()  # Raise an exception for HTTP errors
        #     data = response.json()
        #     logging.info(f"Received data from leader for key: {key}")
        #     return jsonify(data)
        # except requests.exceptions.RequestException as e:
        #     logging.error(f"Failed to retrieve data from leader for key: {key}, error: {e}")
        #     return jsonify({"error": "Failed to retrieve data from leader"})

 
    
    elif request.method == 'POST':
        key = request.args.get('key')
        value = request.args.get('value')
        
        if not (key and value):
            logging.error('No data given.')
            return 'No data given.', 422

        inserted_data = cacheNode.insert(key, value)

        logging.info(f'Data inserted for key: {key}')
        return 'Data inserted successfully.', 201
    else:

        logging.error('Internal Server Error.')
        return 'Internal Server Error.', 501

    
if __name__ == '__main__':
    cacheNode.start()

    cacheNode.zkClient.clear_ephemeral_nodes()

