#!/bin/bash

# 获取当前时间戳
timestamp=$(date +"%Y%m%d%H%M%S")

# 执行命令并提取 pod 名称
pod_names=$(kubectl get pods -n openfaas-fn | grep zjy-2n-product-purchase | awk '{print $1}')

# 初始化 container_ids 列表
container_ids=()

# 遍历 pod_names，提取 Container ID
for pod_name in $pod_names; do
    container_id=$(kubectl describe po $pod_name -n openfaas-fn | grep "Container ID" | awk '{print $3}' | cut -c 14-25)
    container_ids+=("$container_id")
done

# 输出 container_ids 列表
echo "${container_ids[@]}"

# 创建日志目录
log_dir="output/benign-${timestamp}"
mkdir -p "$log_dir/net"
mkdir -p "$log_dir/sysdig"

# echo "-------------------------------------------"
# echo "Start running Sysdig -p ..."
# sudo sysdig -p "*%evt.datetime#%proc.name#%thread.tid#%proc.pid#%proc.vpid#%evt.dir#%evt.type#%fd.name#%proc.ppid#%proc.exepath#%evt.rawres#%container.id#%container.name#%evt.info" \
# "(container.id=${container_ids[0]} or container.id=${container_ids[1]} or container.id=${container_ids[2]} or container.id=${container_ids[3]}) and \
# (evt.type=open or evt.type=openat or evt.type=read or evt.type=write or evt.type=sendto or evt.type=recvfrom or evt.type=execve or evt.type=fork or evt.type=clone or evt.type=bind or evt.type=listen or evt.type=connect or evt.type=accept or evt.type=accept4 or evt.type=chmod or evt.type=connect)" \
# >> "${log_dir}/sysdig/sysdig.log" &
# pid1=$!
# echo $pid1

echo "Start running http-parse-complete ..."
sudo python3.5 ./http-parse-complete.py > "${log_dir}/net/net.log" &
pid2=$!
echo $pid2


sleep 2
pid3=$(pgrep -f "python3.5 ./http-parse-complete.py")
echo $pid3

# sleep 2
# pid4=$(pgrep -f "sysdig -p")
# echo $pid4

cleanup() {
    echo "Terminating processes..."
    # sudo kill -9 $pid1 $pid2 $pid3 $pid4
    sudo kill -9 $pid2 $pid3
    echo "Processes terminated."
}
trap cleanup SIGINT

# 生成erinyes配置
bash update-config.sh

bash perftest_200.sh 31112 ./result-erinyes.csv zjy-2n-product-purchase

sleep 5
echo "Requests send finished. Cleaning up..."
cleanup

chown -R thu1:thu1 "$log_dir"

if [ -n "$rename" ]; then
    new_log_dir="output/${data_attack_type}-${rename}-${timestamp}"
    mv "$log_dir" "$new_log_dir"
fi

# 捕捉 SIGINT 信号，并调用 cleanup 函数
# wait $pid1 $pid2
wait $pid2
