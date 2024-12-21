#! /bin/bash

services='cc-db zch-2n-product-purchase-authorize-cc product-purchase-authorize-cc product-purchase product-purchase-get-price product-purchase-publish zjy-2n-product-purchase-authorize-cc zjy-2n-product-purchase zjy-2n-product-purchase-get-price zjy-2n-product-purchase-publish zch-2n-product-purchase escapeserver2'
for service in $services
do
	kubectl delete --wait=true service/$service deployment.apps/$service -n openfaas-fn
done