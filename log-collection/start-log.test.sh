#!/bin/bash

graph_strategy="split"

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --n_benign) n_benign="$2"; shift ;;
        --n_attack) n_attack="$2"; shift ;;
        --total_time) total_time="$2"; shift ;;
        --data_attack_type) data_attack_type="$2"; shift ;;
        --graph_strategy) graph_strategy="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ -z "$n_benign" || -z "$n_attack" || -z "$total_time" || -z "$data_attack_type" ]]; then
    echo "Error: One or more arguments are empty."
    exit 1
else
    echo "All arguments are set."
fi

# 生成erinyes配置
bash update-config.sh

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

# 获取当前时间戳
timestamp=$(date +"%Y%m%d%H%M%S")

# 要查找的容器名称列表
out_name=$data_attack_type
container_names=("jinyuzhu/zjy-2n-product-purchase-publish" "jinyuzhu/zjy-2n-product-purchase" "jinyuzhu/zjy-2n-product-purchase-get-price" "jinyuzhu/zjy-2n-product-purchase-authorize-cc")
container_images=()

# 创建日志目录
log_dir="output/${out_name}-${timestamp}"
mkdir -p "$log_dir/net"
mkdir -p "$log_dir/sysdig"

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
        echo "-------------------------------------------"
    else
        echo "No matching container found for name: $container_name"
        echo "-------------------------------------------"
    fi
done

# 打印找到的容器镜像
for image in "${container_images[@]}"; do
    echo "$image"
done
