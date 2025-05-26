#!/bin/bash

cd /

./YCSB-compile/bin/ycsb.sh load mongodb -s -P YCSB-compile/workloads/workloadc -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadc -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test > /app/result/outputTERC-mongodb.txt
./YCSB-compile/bin/ycsb.sh load couchdb -s -P YCSB-compile/workloads/workloadc-couchdb
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadc-couchdb > /app/result/outputTERC-couchdb.txt

./YCSB-compile/bin/ycsb.sh load mongodb -s -P YCSB-compile/workloads/workloadi -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test2
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadi -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test2 > /app/result/outputTERI-mongodb.txt
./YCSB-compile/bin/ycsb.sh load couchdb -s -P YCSB-compile/workloads/workloadi-couchdb
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadi-couchdb > /app/result/outputTERI-couchdb.txt


# MongoDB custom
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest1 -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest1 > /app/result/outputTER1-read-mongodb.txt
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest1Scan -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest1 > /app/result/outputTER1-scan-mongodb.txt
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest2 -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest2 > /app/result/outputTER2-read-mongodb.txt
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest2Scan -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest2 > /app/result/outputTER2-scan-mongodb.txt
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest3 -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest3 > /app/result/outputTER3-read-mongodb.txt
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/workloadForest3Scan -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest3 > /app/result/outputTER3-scan-mongodb.txt

# CouchDB custom
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest1-couchdb > /app/result/outputTER1-read-couchdb.txt
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest1Scan-couchdb > /app/result/outputTER1-scan-couch.txt
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest2-couchdb > /app/result/outputTER2-read-couchdb.txt
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest2Scan-couchdb > /app/result/outputTER2-scan-couch.txt
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest3-couchdb > /app/result/outputTER3-read-couchdb.txt
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/workloadForest3Scan-couchdb > /app/result/outputTER3-scan-couch.txt