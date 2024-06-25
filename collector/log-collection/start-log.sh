#!/bin/bash

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --n_benign) n_benign="$2"; shift ;;
        --n_attack) n_attack="$2"; shift ;;
        --total_time) total_time="$2"; shift ;;
        --data_attack_type) data_attack_type="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

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

echo "-------------------------------------------"
echo "Start running Sysdig -p ..."
sudo sysdig -p "*%evt.datetime#%proc.name#%thread.tid#%proc.pid#%proc.vpid#%evt.dir#%evt.type#%fd.name#%proc.ppid#%proc.exepath#%evt.rawres#%container.id#%container.name#%evt.info" \
"container.id!=host and container.name!=<N/A> and (container.image=${container_images[0]} or container.image=${container_images[1]} or container.image=${container_images[2]} or container.image=${container_images[3]}) and \
(evt.type=open or evt.type=openat or evt.type=read or evt.type=write or evt.type=sendto or evt.type=recvfrom or evt.type=execve or evt.type=fork or evt.type=clone or evt.type=bind or evt.type=listen or evt.type=connect or evt.type=accept or evt.type=accept4 or evt.type=chmod or evt.type=connect)" \
>> "${log_dir}/sysdig/sysdig.log" &
pid1=$!
echo $pid1

echo "Start running http-parse-complete ..."
# sudo python3.5 ./http-parse-complete.py >> "${log_dir}/net.log" &
sudo python3.5 ./http-parse-complete.py | jq -r '"UUID: \(.payload | capture("(?i)uuid: (?<uuid>[^\r]*)").uuid) \(. | tojson)"' | while read -r line; do
    uuid=$(echo $line | awk '{print $2}')
    log=$(echo $line | sed 's/UUID: [^ ]* //')
    echo $log >> "${log_dir}/net/${uuid}.log"
done &
pid2=$!
echo $pid2

sleep 2
pid3=$(pgrep -f "python3.5 ./http-parse-complete.py")
echo $pid3

sleep 2
pid4=$(pgrep -f "sysdig -p")
echo $pid4

cleanup() {
    echo "Terminating processes..."
    sudo kill -9 $pid1 $pid2 $pid3 $pid4
    echo "Processes terminated."
    exit 0
}
trap cleanup SIGINT

# 运行 Python 脚本，并传递参数
python3.9 run_lab.py --n_benign "$n_benign" --n_attack "$n_attack" --total_time "$total_time" --data_attack_type "$data_attack_type" --metadata_out_path "$log_dir"
python3.9 sysdig-splitter.py --sysdig-path "${log_dir}/sysdig/sysdig.log"
rm -f "${log_dir}/sysdig/sysdig.log"
sleep 5

cleanup

# 捕捉 SIGINT 信号，并调用 cleanup 函数
wait $pid1 $pid2
