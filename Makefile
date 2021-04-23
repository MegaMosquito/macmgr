# Container that manages my MAC address database

DOCKERHUB_ID:=ibmosquito
NAME:="macmgr"
VERSION:="1.0.0"

# Docker bridge (private virtual) network for local container comms
NETNAME:=couchdbnet
ALIAS:=macmgr

defaut: build run

build:
	docker build -t $(DOCKERHUB_ID)/$(NAME):$(VERSION) .

dev: stop
	docker run -it -v `pwd`:/outside \
	  --name ${NAME} \
          -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
          -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
          -e MY_COUCHDB_CLIENT_ADDRESS=$(MY_COUCHDB_CLIENT_ADDRESS) \
          -e MY_COUCHDB_HOST_PORT=$(MY_COUCHDB_HOST_PORT) \
          --net $(NETNAME) --net-alias $(ALIAS) \
	  $(DOCKERHUB_ID)/$(NAME):$(VERSION) /bin/bash

run: stop
	docker run -d \
	  --name ${NAME} \
	  --restart unless-stopped \
          -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
          -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
          -e MY_COUCHDB_CLIENT_ADDRESS=$(MY_COUCHDB_CLIENT_ADDRESS) \
          -e MY_COUCHDB_HOST_PORT=$(MY_COUCHDB_HOST_PORT) \
          --net $(NETNAME) --net-alias $(ALIAS) \
	  $(DOCKERHUB_ID)/$(NAME):$(VERSION)

push:
	docker push $(DOCKERHUB_ID)/$(NAME):$(VERSION) 

stop:
	@docker rm -f ${NAME} >/dev/null 2>&1 || :

clean:
	@docker rmi -f $(DOCKERHUB_ID)/$(NAME):$(VERSION) >/dev/null 2>&1 || :

.PHONY: build dev run push stop clean
