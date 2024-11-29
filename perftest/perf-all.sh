bash ../scene/tearHRAlastor.sh
bash ../scene/tearHR.sh

# cd ../scene && bash ./deployHR.sh && cd ../perftest
# bash start-log-vanilla.sh
# bash ../scene/tearHR.sh

# sleep 10

cd ../scene && bash ./deployHR.sh && cd ../perftest
bash start-log-erinyes.sh
bash ../scene/tearHR.sh

sleep 10

# cd ../scene && bash ./deployHRAlastor.sh && cd ../perftest
# bash start-log-alastor.sh
# bash ../scene/tearHRAlastor.sh

# python3 perf.py