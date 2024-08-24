#!/bin/bash

container_names=("jinyuzhu/zjy-2n-product-purchase-publish" "jinyuzhu/zjy-2n-product-purchase" "jinyuzhu/zjy-2n-product-purchase-get-price" "jinyuzhu/zjy-2n-product-purchase-authorize-cc")
container_images=()

# 遍历容器名称列表
for container_name in "${container_names[@]}"; do
    echo "Searching for container: $container_name"

    # 使用 docker ps 和 grep 全字匹配容器名称
    container_id=$(sudo docker ps --filter "ancestor=$container_name" --format "{{.ID}}")

    if [ -n "$container_id" ]; then
        echo "Found container ID: $container_id for container name: $container_name"
        # 获取容器信息
        image=$(sudo docker inspect "$container_id" | grep -o '"Image": ".*"' | sed -n '2p' | awk -F': ' '{print $2}' | tr -d '"')
        container_images+=("$image")
        echo $image
        echo "-------------------------------------------"
    else
        echo "No matching container found for name: $container_name"
        echo "-------------------------------------------"
    fi
done