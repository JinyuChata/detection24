#! /bin/bash

services='zjy-alastor-2n-product-purchase-authorize-cc zjy-alastor-2n-product-purchase zjy-alastor-2n-product-purchase-get-price zjy-alastor-2n-product-purchase-publish'
for service in $services
do
	kubectl delete --wait=true service/$service deployment.apps/$service -n openfaas-fn
done

echo 'waiting for hello-retail to down...'
sleep 30