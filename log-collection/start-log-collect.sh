#!/bin/bash

graph_strategy="split"

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --n_per) n_per="$2"; shift ;;
        --graph_strategy) graph_strategy="$2"; shift ;;
        --rename) rename="$2"; shift ;;
        --disable_benign) disable_benign="$2"; shift ;;   # 默认false
        --typ) typ="$2"; shift ;;
        --total_time) total_time="$2"; shift ;;  # 是否并发，如若并发总时间为多少
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ -z "$n_per" ]]; then
    echo "Error: One or more arguments are empty."
    exit 1
else
    echo "All arguments are set."
fi

if [ -z "$disable_benign" ]; then
    disable_benign="false"
fi

echo $disable_benign

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

# 获取当前时间戳
timestamp=$(date +"%Y%m%d%H%M%S")


# 执行命令并提取 pod 名称
pod_names=$(kubectl get pods -n openfaas-fn | grep purchase | awk '{print $1}')

# 初始化 container_ids 列表
container_ids=()

# 遍历 pod_names，提取 Container ID
for pod_name in $pod_names; do
    container_id=$(kubectl describe po $pod_name -n openfaas-fn | grep "Container ID" | awk '{print $3}' | cut -c 14-25)
    container_ids+=("$container_id")
done

# 输出 container_ids 列表
echo "${container_ids[@]}"

data_attack_type="fused"

# 创建日志目录
log_dir="output/${data_attack_type}-${timestamp}"
mkdir -p "$log_dir/net"
mkdir -p "$log_dir/sysdig"

echo "-------------------------------------------"
echo "Start running Sysdig -p ..."
sudo sysdig -p "*%evt.datetime#%proc.name#%thread.tid#%proc.pid#%proc.vpid#%evt.dir#%evt.type#%fd.name#%proc.ppid#%proc.exepath#%evt.rawres#%container.id#%container.name#%evt.info" \
"(container.id=${container_ids[0]} or container.id=${container_ids[1]} or container.id=${container_ids[2]} or container.id=${container_ids[3]}) and \
(evt.type=open or evt.type=openat or evt.type=read or evt.type=write or evt.type=sendto or evt.type=recvfrom or evt.type=execve or evt.type=fork or evt.type=clone or evt.type=bind or evt.type=listen or evt.type=connect or evt.type=accept or evt.type=accept4 or evt.type=chmod or evt.type=connect)" \
>> "${log_dir}/sysdig/sysdig.log" &
pid1=$!
echo $pid1

echo "Start running http-parse-complete ..."
sudo python3 ./http-parse-complete.py > "${log_dir}/net/net.log" &
pid2=$!
echo $pid2


sleep 2
pid3=$(pgrep -f "python3 ./http-parse-complete.py")
echo $pid3

sleep 2
pid4=$(pgrep -f "sysdig -p")
echo $pid4

cleanup() {
    echo "Terminating processes..."
    sudo kill -9 $pid1 $pid2 $pid3 $pid4
    # echo "terminate scene: "
    # bash ../scene/tearHR.sh
    echo "Processes terminated."
}
trap cleanup SIGINT

# echo "-------------------------------------------"
# echo "start scene: "
# original_pwd=$(pwd)
# cd ../scene
# bash ./deployHR.sh
# sleep 20
# kubectl get pods -A | grep purchase
# cd "$original_pwd"
# echo "-------------------------------------------"

# 生成erinyes配置
bash update-config.sh

# 运行 Python 脚本，并传递参数
# total_time 总时间; n_per 每类benign/attack发几次; typ benign or attack
# 并发执行: total_time设为总时间
# 顺序执行: total_time设为0
python3 run_lab_collect.py --metadata_out_path "$log_dir" --n_per "$n_per" --typ "$typ" --total_time $total_time

sleep 5
echo "Requests send finished. Cleaning up..."
cleanup

# 分割日志
if [ "$graph_strategy" == "split" ]; then
  python3 sysdig-splitter.py --sysdig-path "${log_dir}/sysdig/sysdig.log"
  python3 split-http.py --d "${log_dir}"
  sleep 5
fi

# 运行图生成脚本
if [ "$graph_strategy" == "split" ]; then
  python3 generate-dot.py "$log_dir" "$graph_strategy" "$disable_benign"
fi
# python3 generate-dot.py "$log_dir" "all" "false"
# python3.9 prov.py "$log_dir" erinyes

chown -R thu2:thu2 "$log_dir"

if [ -n "$rename" ]; then
    new_log_dir="output/${data_attack_type}-${rename}-${timestamp}"
    mv "$log_dir" "$new_log_dir"
fi

# 捕捉 SIGINT 信号，并调用 cleanup 函数
wait $pid1 $pid2
