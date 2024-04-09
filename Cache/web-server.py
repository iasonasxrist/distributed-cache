from flask import Flask, request, jsonify
from main import LRUCache
import os
import logging
from kazoo.client import KazooClient

app = Flask(__name__)

zk_hosts = 'localhost:2181'
zk_path = '/distributed-cache/services'
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize data and cache
data = {}
port = os.getenv("PORT")
cache = LRUCache(10)


zk = KazooClient(hosts=zk_hosts)
zk.start()

@app.route('/register')
def zk_register():
    service_data = {
        'address': 'localhost',  
        'port': port 
    }

    zk.ensure_path(zk_path)
    zk.create(zk_path + '/instance', "node"+str(port), ephemeral=True)
    return 'Registered with zk'
    

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
        return 'Data inserted successfully.', 201
    else:
        logging.error('Internal Server Error.')
        return 'Internal Server Error.', 501

if __name__ == '__main__':
    app.run(debug=True, port=port)
