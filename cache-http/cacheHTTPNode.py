from flask import Flask
from zookeeper.zookeeperClient import zookeeperClient
import logging
import time
import os
import socket

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# HOST is provided by docker and refers to the hostname of the container
HOSTNAME = os.getenv('HOSTNAME', 'localhost') 
REGISTRATION_ZK_PATH = '/registeredCacheNodes'
ZOOKEEPER_HOST = os.getenv('ZOOKEEPER_HOST', 'zookeeper:2181') 

class CacheHTTPNode:
    def __init__(self) -> None:
        self.zkClient = zookeeperClient(hosts = ZOOKEEPER_HOST)
    
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
            pass
            # update local cache
            # replicate
        else:
            # forward message to master getHostNameOfCacheLeader()
            pass
        
        pass
    
    def get(self, key):
        pass
        
     
            
    
cacheNode= CacheHTTPNode()    

@app.route('/')
def insert():
    return cacheNode.insert(1,1)

@app.route('/')
def get():
    return cacheNode.get(1)

    
if __name__ == '__main__':
    cacheNode.start()
