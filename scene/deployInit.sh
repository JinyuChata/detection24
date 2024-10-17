#! /bin/bash

set -e -o pipefail

export OPENFAAS_URL=http://127.0.0.1:31112

#echo -n $PASSWORD | faas-cli login --password-stdin

#echo 'deploying sql database'
#kubectl apply -f ./mysql.yaml

#echo 'waiting for mysql to come up...'
#sleep 30

#echo 'initializing up database'
#kubectl run --namespace=openfaas-fn --restart=Never --image=mysql:5.6 mysql-client -- mysql -h mysql -ppass -e "CREATE DATABASE IF NOT EXISTS helloRetail"
#sleep 5
#kubectl delete pod mysql-client --namespace=openfaas-fn

echo 'Deploying cc-db'
kubectl apply -f ./cc-db.yaml

echo 'waiting for database to come up...'
sleep 30

echo 'deploying attack server'
kubectl apply -f ./attackserver.yaml

echo 'waiting for attack server to come up...'
sleep 30