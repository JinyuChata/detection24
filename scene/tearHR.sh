#! /bin/bash

services='zjy-2n-product-purchase-authorize-cc zjy-2n-product-purchase zjy-2n-product-purchase-get-price zjy-2n-product-purchase-publish'
for service in $services
do
	kubectl delete --wait=true service/$service deployment.apps/$service -n openfaas-fn
done