bash ../scene/tearHRAlastor.sh
bash ../scene/tearHR.sh

echo "==== erinyes ===="
cd ../scene && bash ./deployHR.sh && cd ../perftest
loadfiles='modify benign leak warm_download'
for loadfile in $loadfiles
do
    echo "===== Benchmarking $loadfile"
    multitime -n 20 curl "http://127.0.0.1:31112/function/zjy-2n-product-purchase" -H "Content-type:application/json" -X POST -d "@loadfiles/$loadfile.json" -s -o /dev/null
done
bash ../scene/tearHR.sh

echo "==== alastor ===="
cd ../scene && bash ./deployHRAlastor.sh && cd ../perftest
loadfiles='modify benign leak warm_download'
for loadfile in $loadfiles
do
    echo "===== Benchmarking $loadfile"
    multitime -n 20 curl "http://127.0.0.1:31112/function/zjy-alastor-2n-product-purchase" -H "Content-type:application/json" -X POST -d "@loadfiles/$loadfile.json" -s -o /dev/null
done
bash ../scene/tearHR.sh