from flask import Flask, jsonify, request
from kazoo.client import KazooClient, KazooState
from kazoo.retry import KazooRetry
from kazoo.exceptions import NoNodeError
import logging
import time
import requests
import os
import socket
from main import LRUCache
app = Flask(__name__)


kz_retry = KazooRetry(max_tries=1000, delay=0.5, backoff=2)
zk_path = '/distributed-cache/services'
cache = LRUCache(10)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

zk = KazooClient(hosts=os.getenv("ZOOKEEPER_HOSTS"), connection_retry=kz_retry, command_retry=kz_retry)

def start_with_retries(max_retries=15, retry_delay=10):
    for i in range(max_retries):
        try:
            zk.start()
            break  # Exit loop if ZooKeeper connection is successful
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise Exception("Could not connect to ZooKeeper after multiple attempts") from e

start_with_retries()

@zk.add_listener
def my_listener(state):
    if state == KazooState.LOST:
        logging.warning("Connection to ZooKeeper lost")
    elif state == KazooState.SUSPENDED:
        logging.warning("Connection to ZooKeeper suspended")
    else:
        logging.info("Connected to ZooKeeper")



def watch_leader():
    try:
        @zk.ChildrenWatch("/web_instances")
        def watch_leader(children):
            if children:
                children.sort()
                leader_path = "/web_instances/" + children[0]
                leader_data, _ = zk.get(leader_path)
                logging.info("Current leader: %s", leader_data.decode())
    except Exception as e:
        logging.error("Error in watching leader: %s", e)

# Start the leader election and watch processes
zk.ensure_path("/web_instances")
zk.create("/web_instances/instance_", ephemeral=True, sequence=True, value = socket.gethostbyname(socket.gethostname()).encode() )
watch_leader()

@app.route('/')
def hello():
    # Register this instance with Kazoo
    zk.create("/web_instances/instance_", ephemeral=True, sequence=True)
    return "Hello, world!"



@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        key = request.args.get('key')
        if key is None:
            logging.error('No key was given.')
            return 'No key was given.', 422 
        cached_data = cache.get(key)
        logging.info(f'Retrieved data for key: {key}')
        return jsonify(cached_data)
    
    elif request.method == 'POST':

        key = request.form.get('key')
        val = request.form.get('val')
        
        if not (key and val):
            logging.error('No data given.')
            return 'No data given.', 422

        inserted_data = cache.set(key, val)
        logging.info(f'Data inserted for key: {key}')


        # Replicate data to child replicas asynchronously
        replicate_data_to_children_async(key, val)
        
        return 'Data inserted successfully.', 201
    
    else:
        logging.error('Internal Server Error.')
        return 'Internal Server Error.', 501
    


# Function to replicate data asynchronously
def replicate_data_to_child_async(replica_path, key, val):
    try:
        replica_data, _ = zk.get(replica_path)
        logging.info("Replicated data to replica %s: %s", replica_path, replica_data.decode())
        # You can implement the logic to replicate data to the child replica here
    except Exception as e:
        logging.error("Error replicating data to child: %s", e)


def replicate_data_to_children_async(key, val):
    try:
        children = zk.get_children("/web_instances")
        logging.info("chiuldren", children)
        if children:
            tasks = []
            for child in children:
                logging.info("chikld",child)
                replica_path = "/web_instances/" + child
                logging.info(child, replica_path)

                replica_data, _ = zk.get(replica_path)
                logging.info("Data Replication : %s", replica_data.decode())

                
                response = requests.post(f"http://{replica_data.decode():8000}/data", data={'key': key,'value':val})
   
            if response.status_code == 200:
                logging.info("Data replicated to child node %s successfully", replica_data.decode())
            else:
                logging.error("Failed to replicate data to child node %s. Status code: %s", replica_data.decode(), response.status_code)

    except Exception as e:
        logging.error("Error replicating data to child node %s: %s", replica_data.decode(), e)



if __name__ == '__main__':
    app.run()
