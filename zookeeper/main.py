from kazoo.client import KazooClient
from kazoo.client import KeeperState
import os
import json
import time


class ZooKeeperClient:

    def __init__(self, port, host):
        self.zk = KazooClient(hosts=':'.join([os.getenv("host"), str(os.getenv("port"))]))
        self.zk.add_listener(self.watch_for_ro)
        self.zk.start()

    
    def createZnode(self, key, value, ttl=None):
        """
        Create a znode for each cache replica
        """
        self.zk.ensure_path("/caches")
        self.zk.create(f"/cache/{key}", json.dumps({"value":value}), ttl=ttl)
        return
    
    def get(self, key):
        """
        Get znode's data
        """
        value, _ = self.zk.get(f"/cache/{key}")
        return json.loads(value.decode())["value"]

    def IsZnodeExists(self, key):
         """
         Check if a znode exists
         """
         return self.zk.exists(f"/cache/{key}")

    def delete(self, key):
        self.zk.delete("f/cache/{key}")
        time.sleep(2)
        if not self.IsZnodeExists(key):
            print("Deleted Succesfully")
            return

    def watch_changes(self, key, callback):
        """
            Keep Monitoring the incoming changes
        """
        @self.zk.DataWatch("f/cache/{key}")
        def watch_data_func(data, stat):
            if data:
                print("Cache metadata changed:", data)
                value = json.loads(data.decode())["value"]


    def watch_for_ro(self, state):
        """
        Check status of Zookeepper
        """
        if state == KeeperState.CONNECTED:
            if self.zk.client_state == KeeperState.CONNECTED_RO:
                print("Read only mode!")
            else:
                print("Read/Write mode!")


    def close(self):
        self.zk.stop()
        self.zk.close()