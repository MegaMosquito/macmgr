FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-dev python3-pip git

# Install couchdb interface
RUN pip3 install couchdb
RUN pip3 install pythonping

# Install convenience tools (may omit these in production)
#RUN apk --no-cache --update add vim curl jq
RUN apt install -y vim curl jq

# Copy over the macmgr files
COPY ./src/*.py /macmgr/

# Start up the daemon process
CMD python3 macmgr.py >/dev/null 2>&1

