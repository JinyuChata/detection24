#!/bin/bash

set -e -o pipefail

export OPENFAAS_URL=http://localhost:31112
# export PATH=$PATH:/home/ubuntu/.arkade/bin/

echo 'deploying hello-retail'
faas-cli login -p 4A4uK1vkGIwK --gateway $OPENFAAS_URL
faas-cli deploy -f ./hello-retail.yaml --gateway $OPENFAAS_URL

echo 'waiting for hello-retail to come up...'
sleep 30

echo 'ready to test attack hello-retail workflows'