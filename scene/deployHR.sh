#!/bin/bash

set -e -o pipefail

export OPENFAAS_URL=http://127.0.0.1:31112

echo 'deploying hello-retail'
faas-cli deploy -f ./hello-retail.yaml
# faas-cli deploy -f ./hello-retail-cfattack.yaml
# faas-cli deploy -f ./hello-retail-escape.yaml

echo 'waiting for hello-retail to come up...'
sleep 30

#echo 'Starting log server'
#cd ../tracereceiver
#python fileserver.py &
echo 'ready to test attack hello-retail workflows'

# Normal execution
# curl -d "@sample-input.json" -H "Content-Type: application/json" -X POST 'http://127.0.0.1:31112/function/product-purchase'

# Attack execution
#curl -d "@sample-input.json" -H "Content-Type: application/json" -H "X-Compromised: one" -X POST 'http://127.0.0.1:31112/function/product-purchase'
#curl -d "@sample-input.json" -H "Content-Type: application/json" -H "X-Compromised: two" -X POST 'http://127.0.0.1:31112/function/product-purchase'