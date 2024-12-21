#! /bin/bash

services='product-purchase-authorize-cc product-purchase place-order validate-cart create-order process-payment update-stock check-stock calculate-discount verify-payment'
for service in $services
do
	microk8s kubectl delete --wait=true service/$service deployment.apps/$service -n openfaas-fn
done