#!/bin/bash

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