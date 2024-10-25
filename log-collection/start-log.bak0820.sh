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


SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

# 获取当前时间戳
timestamp=$(date +"%Y%m%d%H%M%S")

# 要查找的容器名称列表
out_name=$data_attack_type
# container_names=("jinyuzhu/zjy-2n-product-purchase-publish" "jinyuzhu/zjy-2n-product-purchase" "jinyuzhu/zjy-2n-product-purchase-get-price" "jinyuzhu/zjy-2n-product-purchase-authorize-cc")
container_images=("jinyuzhu/zjy-2n-product-purchase-publish@sha256:36f7ea54b60de0a660c264496d508a0d6113dd6055fb7627749d924aa2ff590d" "jinyuzhu/zjy-2n-product-purchase@sha256:5b75d956f8aca84471785542011efbf7df7cbb2c1d68b30e5bcd945e639cb31f" "jinyuzhu/zjy-2n-product-purchase-get-price@sha256:054890c19140f43608ce2dc2a513f6583c6ad72aa450ebd3d551692c40fc25eb" "jinyuzhu/zjy-2n-product-purchase-authorize-cc@sha256:eaab7b10599381af9ce493c18e257478df8bd1bd695b549b570a0e5e5eed1cb4")

# 创建日志目录
log_dir="output/${out_name}-${timestamp}"
mkdir -p "$log_dir/net"
mkdir -p "$log_dir/sysdig"

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
if [ "$graph_strategy" == "split" ]; then
    sudo python3.5 ./http-parse-complete.py | jq -r '"UUID: \(.payload | capture("(?i)uuid: (?<uuid>[^\r]*)").uuid) \(. | tojson)"' | while read -r line; do
        uuid=$(echo $line | awk '{print $2}')
        log=$(echo $line | sed 's/UUID: [^ ]* //')
        echo $log >> "${log_dir}/net/${uuid}.log"
    done &
    pid2=$!
    echo $pid2
else
    sudo python3.5 ./http-parse-complete.py > "${log_dir}/net/net.log" &
    pid2=$!
    echo $pid2
fi

sleep 2
pid3=$(pgrep -f "python3.5 ./http-parse-complete.py")
echo $pid3

sleep 2
pid4=$(pgrep -f "sysdig -p")
echo $pid4

cleanup() {
    echo "Terminating processes..."
    sudo kill -9 $pid1 $pid2 $pid3 $pid4
    echo "terminate scene: "
    bash ../scene/tearHR.sh
    echo "Processes terminated."
}
trap cleanup SIGINT

echo "-------------------------------------------"
echo "start scene: "
original_pwd=$(pwd)
cd ../scene
bash ./deployHR.sh
sleep 20
kubectl get pods -A | grep purchase
cd "$original_pwd"
echo "-------------------------------------------"

# 生成erinyes配置
bash update-config.sh

# 运行 Python 脚本，并传递参数
python3.9 run_lab.py --n_benign "$n_benign" --n_attack "$n_attack" --total_time "$total_time" --data_attack_type "$data_attack_type" --metadata_out_path "$log_dir"

sleep 5
echo "Requests send finished. Cleaning up..."
cleanup

# 分割Sysdig日志
if [ "$graph_strategy" == "split" ]; then
  python3.9 sysdig-splitter.py --sysdig-path "${log_dir}/sysdig/sysdig.log"
  # rm -f "${log_dir}/sysdig/sysdig.log"
  sleep 5
fi

# 运行图生成脚本
python3.9 generate-dot.py "$log_dir" "$graph_strategy"


# 捕捉 SIGINT 信号，并调用 cleanup 函数
wait $pid1 $pid2


