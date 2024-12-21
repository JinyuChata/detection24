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

cc_db_service='cc-db'
# 构建并推送 dattapubali/ 命名空间的 cc-db 服务
cc_db_tag="dattapubali/${cc_db_service}:latest"
echo "Building $cc_db_tag"
(cd $cc_db_service && docker build -f Dockerfile -t $cc_db_tag .)
#docker push $cc_db_tag

#for service in $services
#do
#	old_tag="${service}:latest"
#	new_tag="dattapubali/${service}:latest-attack"
#	echo Retagging $old_tag to $new_tag
#	docker tag $old_tag $new_tag
#done