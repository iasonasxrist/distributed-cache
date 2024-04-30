from flask import Flask, jsonify, request
from zookeeper.zookeeperClient import zookeeperClient
from cache.cache import LRUCache
import logging
import time
import os
import socket
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

    
    
    def insert(self, key, value, senderAddress) -> None:
        if self.amICacheLeader():
            #I am leader
            # update local cache
            self.cache.set(key, value)
            # replicate
            followers = self.getHostNameOfCacheFollowers()
            if followers is None:
                logging.info("No nodes were found to send data.")
                return None
            
            addressesOfFollowers = []
            toSend = {key : value}

            for follower in followers:
                try:
                    data, _ = self.zkClient.get(follower)
                    addressesOfFollowers.append(data.decode())
                except Exception as e:
                    logging.info(f"Node {follower} didn't have a record in zk.")

            for address in addressesOfFollowers:
                try:
                    response = requests.post(address, json=toSend)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                except requests.exceptions.HTTPError as http_err:
                    logging.info(f'Node {address}: HTTP error occurred: {http_err}')
                except requests.exceptions.ConnectionError as conn_err:
                    logging.info(f'Node {address}: Connection error occurred: {conn_err}')
                except requests.exceptions.Timeout as timeout_err:
                    logging.info(f'Node {address}: Request timed out: {timeout_err}')
                except requests.exceptions.RequestException as req_err:
                    logging.info(f'Node {address}: An error occurred: {req_err}')
        else:
            # I am a follower
            # If the leader sent me something I put it in my cache. 
            # If someone else sent me something I send it to the leader
        
            leaderAddress = self.getHostNameOfCacheLeader()
            address, _ = self.zkClient.get(leaderAddress)
            #I check the sender address. If sender is not the leader:

            url = leaderAddress + "/data"
            if senderAddress != leaderAddress:
                response = requests.post(url, toSend)

                if response.status_code != 200:
                    logging.info("Something may cause unsuccesfull request!")

            #If sender is leader then I update.
            self.cache.set(key, value)
    
    def get(self, key):
        pass
        
     
            
    
cacheNode= CacheHTTPNode()    

@app.route('/data', methods=['GET', 'POST'])
def handle_data(self):
    if request.method == 'GET':
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
        cached_data = self.cache.get(key)

        logging.info(f'Retrieved data for key: {key}')
        return jsonify(cached_data)
    
    elif request.method == 'POST':
        key = request.args.get('key')
        val = request.args.get('val')
        
        if not (key and val):
            logging.error('No data given.')
            return 'No data given.', 422

        senderAddr = request.remote_addr

        inserted_data = cacheNode.insert(key, val, senderAddr)
        logging.info(f'Data inserted for key: {key}')
        return 'Data inserted successfully.', 201
    else:
        logging.error('Internal Server Error.')
        return 'Internal Server Error.', 501

    
if __name__ == '__main__':
    cacheNode.start()
