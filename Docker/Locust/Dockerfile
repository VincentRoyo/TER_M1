FROM locustio/locust

RUN pip install pymongo

WORKDIR /locust

COPY Api ./Api
COPY Mongo ./Mongo
COPY Couchdb ./Couchdb
COPY locustfile.py .
COPY forest.csv .

