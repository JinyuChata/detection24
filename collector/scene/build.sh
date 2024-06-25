#! /bin/bash

services='zjy-2n-product-purchase-authorize-cc zjy-2n-product-purchase zjy-2n-product-purchase-get-price zjy-2n-product-purchase-publish'

#services='attack-product-purchase'
 docker login -u jinyuzhu -p dckr_pat_CD-LbOjMi4BOF0sWYwHVCoYMKGY


for service in $services
do
	tag="jinyuzhu/${service}:latest"
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