# set -e -o pipefail

arg1=${1:-31112}
arg2=${2:-"./result.csv"}
arg3=${3:-"zjy-alastor-2n-product-purchase"}


rm -rf "./result"

if [ ! -d "./result" ]; then
  mkdir "./result"
fi

export OPENFAAS_URL=http://127.0.0.1:31112

nworker=5
duration=30s

nohup /bin/bash collectmetrics.sh &
pid=$!

for reqpersec in {1,5,10,20,50,100}
do
    echo 'launching hey for load testing'
    ./hey_linux_amd64 -z=$duration -q $reqpersec -c $nworker -m POST -D ./benign.json -H "Content-Type: application/json" "http://127.0.0.1:$arg1/function/$arg3" > ./result/testperf-worker$nworker.reqpersec$reqpersec.txt
done
echo "Stopping collectmetrics.sh..."

# 获取所有 collectmetrics.sh 进程的 PID，并使用 kill 命令停止它们
python3 ./dataparser/parsejson.py ./result/ $arg2
echo "hello"
kill "$pid"
wait "$pid"