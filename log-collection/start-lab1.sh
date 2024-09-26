#!/bin/bash

# # GT
# sudo bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --rename gt --disable_benign true
# # RC1, 1req/sec
# sudo bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --rename rc1 --disable_benign true
# # RC2, 10req/sec
# sudo bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --rename rc2 --disable_benign true
# # RC3, 50req/sec
# sudo bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type modify --graph_strategy split --rename rc3 --disable_benign true

# # GT
# sudo bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type leak --graph_strategy split --rename gt --disable_benign true
# # RC1, 1req/sec
# sudo bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type leak --graph_strategy split --rename rc1 --disable_benign true
# # RC2, 10req/sec
# sudo bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type leak --graph_strategy split --rename rc2 --disable_benign true
# # RC3, 50req/sec
# sudo bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type leak --graph_strategy split --rename rc3 --disable_benign true

# # GT
# sudo bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type warm --graph_strategy split --rename gt --disable_benign true
# # RC1, 1req/sec
# sudo bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type warm --graph_strategy split --rename rc1 --disable_benign true
# # RC2, 10req/sec
# sudo bash start-log.sh --n_benign 18 --n_attack 1 --total_time 2 --data_attack_type warm --graph_strategy split --rename rc2 --disable_benign true
# # RC3, 50req/sec
# sudo bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type warm --graph_strategy split --rename rc3 --disable_benign true

python3 metric.py