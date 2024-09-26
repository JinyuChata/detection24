#!/bin/bash
pods_info=$(kubectl get pods -o custom-columns='NAME:.metadata.name,IP:.status.podIP' -A | grep purchase)
conf_sample_file="erinyes-code/conf/config.yaml.sample"
conf_file="erinyes-code/conf/config.yaml"

echo "# Auto generated from config.yaml.sample." > $conf_file
echo "# DO NOT EDIT" >> $conf_file
cat $conf_sample_file >> $conf_file

# IP
ip_map=""
while read -r line; do
  ip=$(echo "$line" | awk '{print $2}')
  name=$(echo "$line" | awk '{print $1}')
  id=$(echo "$line" | awk '{print $1}' | awk -F'-' '{print $(NF-1)"-"$NF}')
  formatted_name=$(echo "$name" | sed "s/-$id//")
  ip_map+="  $ip: $formatted_name\$$id\n"
done <<< "$pods_info"

ip_map=$(echo "$ip_map" | sed '$s/\\n$//')

sed -i "s|<IPMAP>|$ip_map|g" "$conf_file"

# GATEWAY
gateway_info=$(kubectl get svc -o wide -A | grep gateway)
gateway_map=""
while read -r line; do
  ip=$(echo "$line" | awk '{print $4}')
  gateway_map+="  $ip: true\n"
done <<< "$gateway_info"
gateway_map=$(echo "$gateway_map" | sed '$s/\\n$//')
sed -i "s|<GATEWAYMAP>|$gateway_map|g" "$conf_file" >> "$conf_file"
