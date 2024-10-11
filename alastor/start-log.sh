#!/bin/bash
# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --n_benign) n_benign="$2"; shift ;;
        --n_attack) n_attack="$2"; shift ;;
        --total_time) total_time="$2"; shift ;;
        --data_attack_type) data_attack_type="$2"; shift ;;
        --rename) rename="$2"; shift ;;
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

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

timestamp=$(date +"%Y%m%d%H%M%S")

echo "==== deploy containers"
curr_dir=$(pwd)
# cd ../scene
# bash ../scene/deployHRAlastor.sh
cd $curr_dir

# 获取与 "zjy-alastor-2n-product-purchase" 相关的 pod 列表
# pod_names=$(kubectl get pods -A | grep zjy-alastor-2n-product-purchase | awk '{print $2}')
pod_names=$(kubectl get pods -A | grep 2n-product-purchase | awk '{print $2}')
echo "Pods found: $pod_names"

# 创建日志目录
log_dir="output/${data_attack_type}-${timestamp}"
mkdir -p "$log_dir/raw-tar"
mkdir -p "$log_dir/raw"
mkdir -p "$log_dir/dot"

# 运行 Python 脚本，并传递参数
python3.9 run_lab.py --n_benign "$n_benign" --n_attack "$n_attack" --total_time "$total_time" --data_attack_type "$data_attack_type" --metadata_out_path "$log_dir"
sleep 5

# 循环 pod_names 列表，压缩并拷贝 tar 文件
for pod_name in $pod_names; do
    echo "Processing pod: $pod_name"

    # 压缩 request.alastor 日志文件到 request.alastor.tar
    kubectl exec "$pod_name" -n openfaas-fn -- /bin/sh -c "tar -czf request.alastor.tar request.alastor*" || {
        echo "Failed to compress logs in $pod_name"
        continue
    }

    # 将压缩文件从容器内拷贝到本地 $log_dir/raw-tar 目录
    kubectl cp "openfaas-fn/${pod_name}:/home/app/request.alastor.tar" "$log_dir/raw-tar/${pod_name}.tar.gz" || {
        echo "Failed to copy tar file from $pod_name"
        continue
    }

    # kubectl exec "$pod_name" -n openfaas-fn -- /bin/sh -c "rm -rf request.alastor*" || {
    #     echo "Failed to compress logs in $pod_name"
    #     continue
    # }

    # 解压本地的 tar.gz 文件到 $log_dir/raw 目录
    mkdir -p "$log_dir/raw/${pod_name}" 
    tar -xzf "$log_dir/raw-tar/${pod_name}.tar.gz" -C "$log_dir/raw/${pod_name}" || {
        echo "Failed to extract $log_dir/raw-tar/${pod_name}.tar.gz"
        continue
    }

    echo "Processed logs for $pod_name"
done

curr_dir=$(pwd)

cd ./alastor
go run alastor.go "../$log_dir/raw" "../$log_dir/dot"
cd $curr_dir

# 修改日志目录的权限
chown -R ubuntu:ubuntu "./output"

# 如果提供了 rename 参数，则重命名日志目录
if [ -n "$rename" ]; then
    new_log_dir="output/${data_attack_type}-${rename}-${timestamp}"
    mv "$log_dir" "$new_log_dir"
fi

echo "==== closing old containers"
# bash ../scene/tearHRAlastor.sh