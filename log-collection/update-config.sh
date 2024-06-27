#!/bin/bash
pods_info=$(kubectl get pods -A -o wide | grep purchase)

echo "$pods_info" | while read -r line; do
  # IP
  ip=$(echo "$line" | awk '{print $7}')
  # POD
  name=$(echo "$line" | awk '{print $2}')
  
  # POD_ID
  id=$(echo "$line" | awk '{print $2}' | awk -F'-' '{print $(NF-1)"-"$NF}')
  formatted_name=$(echo "$name" | sed "s/-$id//")
  echo "  $ip: $formatted_name\$$id"
done