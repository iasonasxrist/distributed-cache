from kazoo.client import KazooClient
from kazoo.retry import KazooRetry
from kazoo.exceptions import NoNodeError
from kazoo.client import KazooState
import time 
import logging
import os



logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class zookeeperClient:
    def __init__(self, hosts) -> None:
        self.kz_retry = KazooRetry(max_tries=1000, delay=0.5, backoff=2)
        self.zkClient = KazooClient(hosts=hosts, connection_retry=self.kz_retry, command_retry=self.kz_retry)
        self.clientConnented = False
        try:
            self.start_with_retries()
            self.startConnectionListener()
            self.clientConnented = True
            
        except:
            raise Exception("Zookeeper client failed to be started")
            
    def startConnectionListener(self):
        @self.zkClient.add_listener
        def connectionListener(state):
            if state == KazooState.LOST:
                logging.warning("Connection to ZooKeeper lost")
                self.clientConnented = False
            elif state == KazooState.SUSPENDED:
                logging.warning("Connection to ZooKeeper suspended")
                self.clientConnented = False
            else:
                logging.info("Connected to ZooKeeper")
                self.clientConnented = True

            
        
    def start_with_retries(self, max_retries=15, retry_delay=10):
        for i in range(max_retries):
            try:
                self.zkClient.start()
                break  # Exit loop if ZooKeeper connection is successful
            except Exception as e:
                if i < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception("Could not connect to ZooKeeper after multiple attempts") from e
                
    def registerSequentialZNode(self, path, data):
        try:
            self.zkClient.ensure_path(os.path.dirname(path)) #create s along with subfolders
            self.zkClient.create(path, ephemeral=True, sequence=True, value = data.encode())
        except:
            raise Exception(f"Failed to register path: {path} with data: {data}")
             
    
    def getSortedSubNodes(self, path):
        if self.zkClient.exists(path):
            children = self.zkClient.get_children(path)
            return sorted(children)
        else:
            raise Exception (f"Path : {path} does not exist")
        
    def getZNodeData(self, path):
        if self.zkClient.exists(path):
            logging.info(f" **** My path ****** {path} ")
            data, _ = self.zkClient.get(path)
            logging.info(f"****data*** {data}")
            return data.decode()
        else:
            raise Exception (f"Path : {path} does not exist")
        
        
    def clear_ephemeral_nodes(self):
        """
        Delete ephimeral nodes when service exits
        """
        if self.clientConnented:
            
            try:
                # For example:
                self.zkClient.delete("/registeredCacheNodes", recursive=True)
                logging.info(f"Znodes deleted successfully.")
            except Exception as e:
                print(f"Failed to clear ephemeral nodes: {e}")
    