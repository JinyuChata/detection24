#!/bin/bash

# # GT
# bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type modify --rename gt
# # RC1, 1req/sec
# bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type modify --rename rc1
# # RC2, 10req/sec
# bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type modify --rename rc2
# # RC3, 50req/sec
# bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type modify --rename rc3

# GT
bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type leak --rename gt
# RC1, 1req/sec
bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type leak --rename rc1
# RC2, 10req/sec
bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type leak --rename rc2
# RC3, 50req/sec
bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type leak --rename rc3

# GT
bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type warm --rename gt
# RC1, 1req/sec
bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type warm --rename rc1
# RC2, 10req/sec
bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type warm --rename rc2
# RC3, 50req/sec
bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type warm --rename rc3

# GT
bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type cfattack --rename gt
# RC1, 1req/sec
bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type cfattack --rename rc1
# RC2, 10req/sec
bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type cfattack --rename rc2
# RC3, 50req/sec
bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type cfattack --rename rc3

# # normal
# bash start-log.sh --n_benign 50 --n_attack 0 --total_time 1 --data_attack_type normal --rename rc3



# TODO: To add new scenes, 
# 1. copy one block, uncomment, then modify `data_attack_type`
# 2. add `data_attack_type` to list variable `attacks` in metric.py
# 3. bash start-lab1.sh

# python3 metric.py >> result-lab1-effectiveness.txt