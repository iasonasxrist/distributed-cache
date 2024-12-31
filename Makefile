IMAGE_NAME := zookeeper-host


up :
    docker-compose up --build
    
build:
    docker build -t $(IMAGE_NAME) .

run:
    docker run --name $(IMAGE_NAME) -p 2181:2181 -d $(IMAGE_NAME)
