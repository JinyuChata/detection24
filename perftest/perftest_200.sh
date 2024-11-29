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
reqpersec=40

nohup /bin/bash collectmetrics.sh &
pid=$!
echo 'launching hey for load testing'
./hey_linux_amd64 -z=$duration -q $reqpersec -c $nworker -m POST -D ./benign.json -H "Content-Type: application/json" "http://127.0.0.1:$arg1/function/$arg3" > ./result/testperf-worker$nworker.reqpersec$reqpersec.txt
echo "Stopping collectmetrics.sh..."
python3 ./dataparser/parsejson.py ./result/ $arg2
echo "hello"
kill "$pid"
wait "$pid"