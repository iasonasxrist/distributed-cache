from flask import Flask, jsonify, request, redirect
from zookeeper.zookeeperClient import zookeeperClient
from cache.cache import LRUCache
import logging
import os
import requests
from CircularLinkedList import CircularLinkedList



app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# HOST is provided by docker and refers to the hostname of the container
HOSTNAME = os.getenv('HOSTNAME') 
REGISTRATION_ZK_PATH = '/registeredCacheNodes'
ZOOKEEPER_HOST = os.getenv('ZOOKEEPER_HOST') 
GATEWAY_PORT = os.getenv('GATEWAY_PORT')

class CacheGateway:
    def __init__(self) -> None:
        self.zkClient = zookeeperClient(hosts = ZOOKEEPER_HOST)
        self.current = 0

    def start(self):
        logging.info(f"Starting cache node with HOSTNAME {HOSTNAME}")

        try:
            self.accessToIpList()
            logging.debug("Ips retrieved successfully!")
        except Exception as e:
            return "Service Unavailable", 503
        
        #Init HTTP server
        app.run(host='0.0.0.0', port=GATEWAY_PORT)
        logging.info("Server is up and running")


    def accessToIpList(self)->list:

        # ips = self.zkClient.getHostNameOfAllNodes(REGISTRATION_ZK_PATH)
        ips = self.zkClient.getHostNameOfCacheFollowers(REGISTRATION_ZK_PATH)

        self.circular = CircularLinkedList()
        for ip in ips:
            self.circular.append(ip)

    def getNextNode(self):

        if self.current == 0:
            self.current = self.circular.first_node()

        nextNode = self.circular.get_next_node(self.current)
        logging.debug(f"********new node {nextNode.data} and current {self.current.data}")
        self.current = nextNode
        return nextNode.data
   
cacheGateway = CacheGateway()


@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':

        next_ip = cacheGateway.getNextNode()

        logging.info(f"Ip Receiver is {next_ip}")
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
                
        try:
            # Forward the request to the next node
            response = requests.get(f'http://{next_ip}:5000/data?key={key}')
            response.raise_for_status()
            cached_data = response.json()
            logging.info(f'Retrieved data for key: {key} from {next_ip}')
            return jsonify(cached_data)
        
        except requests.exceptions.RequestException as e:
            logging.error(f'Error forwarding request to {next_ip}: {e}')
            return 'Error retrieving data from node.', 500

    elif request.method == 'POST':
        
        key = request.args.get('key')
        value = request.args.get('value')
        
        if not (key and value):
            logging.error('No data given.')
            return 'No data given.', 422
        
        else:

            leader_hostname = cacheGateway.zkClient.getHostNameOfCacheLeader(path=REGISTRATION_ZK_PATH)
            response = requests.post(f'http://{leader_hostname}:5000/data?key={key}&value={value}')
            
            logging.info(f'Forwared data to leader {leader_hostname}')
            return "Successful sent ", 200


        
    else:
        return 'Internal Server Error.', 501

    
if __name__ == '__main__':
    cacheGateway.start()