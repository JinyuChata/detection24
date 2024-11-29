#! /bin/bash
duration=1500
end=$((SECONDS+duration))
iter=1
rm -f ./result/*
while [ $SECONDS -lt $end ]; do
    kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes > ./result/nodemetrics$iter.json
    kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/openfaas-fn/pods > ./result/podmetrics$iter.json 
    kubectl top nodes > ./result/nodetop$iter.txt
    sar -u -r 1 2 | grep Average: | awk '
    /^Average:/ {
        if (NR == 2) {
        cpu_usage = 100 - $NF;
        print "Average CPU Usage: " cpu_usage "%";
        }
        if (NR == 4) {
        mem_used = $3;
        print "Average Memory Used: " mem_used " KB";
        }
    }
    ' > ./result/top$iter.txt
    # top -b -n 1 | grep -E "^(%|KiB Mem)" | awk '{if(NR==1) print "CPU: " $2 "%"; else print "Memory: " $8 " used"}' > ./result/top$iter.txt
    iter=$((iter+1))
    # sleep 5
done
