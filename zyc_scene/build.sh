#! /bin/bash

services='product-purchase-authorize-cc product-purchase place-order validate-cart create-order process-payment update-stock check-stock calculate-discount verify-payment'

#services='attack-product-purchase'
docker login -u koinikki -p lightningdocker


for service in $services
do
	tag="koinikki/${service}:latest"
	echo Building $tag
	(cd $service && docker build -f Dockerfile.vanilla -t $tag .)
    docker push $tag
done

#for service in $services
#do
#	old_tag="${service}:latest"
#	new_tag="dattapubali/${service}:latest-attack"
#	echo Retagging $old_tag to $new_tag
#	docker tag $old_tag $new_tag
#done