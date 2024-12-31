from flask import Flask, jsonify, request, redirect
from zookeeper.zookeeperClient import zookeeperClient
from cache.cache import LRUCache
import logging
import os
import requests
import time
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
        kazoo = self.zkClient.getObjectOfWatchers()
        
        @kazoo.ChildrenWatch(REGISTRATION_ZK_PATH)
        def watch_children(children):
            logging.warning("Children are now: %s" % children)
            hostnames = self.zkClient.getHostNameOfAllNodes(REGISTRATION_ZK_PATH, children)
            self.circular = CircularLinkedList()
            [self.circular.append(hostname) for hostname in hostnames]

   
cacheGateway = CacheGateway()

def getRequestRec(key,retries=0, max_retries=5):

    nextHostname = cacheGateway.circular.getNext()
    if nextHostname is None:
        return 'All servers are gone.', 503

    if retries >= max_retries:
        return "Max attempts reached!", 503
    
    try:
        # Forward the request to the next node
        response = requests.get(f'http://{nextHostname}:5000/data?key={key}')
        response.raise_for_status()
        cached_data = response.json()
        logging.info(f'Retrieved data for key: {key} from {nextHostname}')
        return jsonify(cached_data)
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error forwarding request to {nextHostname}: {e}')
        return getRequestRec(key, retries=retries+1, max_retries=max_retries)



def LeaderTimeOutSwitch(key, value, retries=0, max_retries=5):
    base_wait_time=2

    while retries < max_retries:
        try:
                    
            leader_hostname = cacheGateway.zkClient.getHostNameOfCacheLeader(path=REGISTRATION_ZK_PATH)
            logging.info(f'Forwarded data to leader {leader_hostname}')
            response = requests.post(f'http://{leader_hostname}:5000/data?key={key}&value={value}')
            response.raise_for_status()
            return "OK", 200

        except requests.exceptions.Timeout:
            logging.error('Timeout error when connecting to leader.408')
        except requests.exceptions.ConnectionError:
           
            logging.error('Connection error when connecting to leader. 599')
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 503:
                logging.error('503 Service Unavailable from leader.')
                return "503 Service Unavailable", 503

        retries += 1
        wait_time = base_wait_time * (2 ** retries)
        logging.info(f'Waiting for {wait_time} seconds before retrying...')
        time.sleep(wait_time)

    logging.error('Max attempts reached! Failed to connect to leader.')
    return "Max attempts reached!", 503
        
@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 

        return getRequestRec(key)

    elif request.method == 'POST':
        
        key = request.args.get('key')
        value = request.args.get('value')
        
        if not (key and value):
            logging.error('No data given.')
            return 'No data given.', 422
        
        else:     
          
          return LeaderTimeOutSwitch(key, value)

    else:
        return 'Internal Server Error.', 501

    
if __name__ == '__main__':
    cacheGateway.start()