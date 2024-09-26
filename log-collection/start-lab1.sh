#!/bin/bash

# GT
sudo bash start-log.sh --n_benign 0 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --rename gt
# RC1, 1req/sec
sudo bash start-log.sh --n_benign 1 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --rename rc1
# RC2, 10req/sec
sudo bash start-log.sh --n_benign 9 --n_attack 1 --total_time 1 --data_attack_type modify --graph_strategy split --rename rc2
# RC3, 50req/sec
sudo bash start-log.sh --n_benign 49 --n_attack 1 --total_time 1 --data_attack_type modify --graph_strategy split --rename rc3
