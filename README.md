# Distributed Cache using single leader and synchronous replication
<img width="1196" alt="image" src="https://github.com/iasonasxrist/distributed-cache/assets/80000902/1f476e37-7f3f-43a4-85c9-99f7bf5cca8f">
# Distributed Cache with Single Leader and Synchronous Replication
# Distributed Cache with Single Leader and Synchronous Replication

## Overview
This project implements a distributed cache system using a single leader architecture with synchronous replication. The system utilizes ZooKeeper for leader election and to manage three replicas of the cache. The cache itself is built using a doubly linked list (DLL) and a hashmap for efficient data storage and retrieval.

## Architecture
The architecture consists of the following components:
1. **Leader**: Responsible for handling read and write requests from clients. Leader is elected using ZooKeeper.
2. **Replicas**: Three replicas are maintained to ensure fault tolerance and data consistency. Replicas replicate data synchronously with the leader.
3. **Cache**: The cache is implemented using a doubly linked list (DLL) and a hashmap. The DLL provides constant time access for both insertion and deletion operations, while the hashmap ensures fast retrieval of data based on keys.
4. **ZooKeeper**: Used for leader election and managing the configuration of the cache system.

## Setup Instructions
1. **Install ZooKeeper**: Follow the installation instructions for ZooKeeper from the official documentation.
2. **Clone the Repository**: Clone this repository to your local machine.
3. **Build and Run**: Build and run the cache system using the provided scripts.
    ./build.sh
    ./run.sh
4. **ZooKeeper Configuration**: Configure ZooKeeper client in `zookeeper.properties` file with appropriate ZooKeeper server addresses.
5. **Start ZooKeeper**: Start ZooKeeper server.
    ./start_zookeeper.sh
6. **Start Cache System**: Start the cache system.
    ./start_cache_system.sh

## Usage
- **Client Interaction**: Clients can interact with the cache system using appropriate client libraries or APIs.
- **Read and Write**: Clients can perform read and write operations on the cache system through the leader.
- **Data Retrieval**: Clients can retrieve data by sending GET requests to the appropriate endpoint `/data`.
- **Fault Tolerance**: In case of leader failure, ZooKeeper will elect a new leader from available replicas.
- **Synchronous Replication**: Replicas synchronously replicate data from the leader to ensure consistency.

## Contribution Guidelines
Contributions to improve the system are welcome. Please follow these guidelines:
- Fork the repository.
- Make your changes.
- Submit a pull request detailing the changes made and any relevant information.

## License
This project is licensed under the MIT License.

