#!/bin/bash

# generate split (benign + attack, split)
sudo bash start-log.sh --n_benign 10 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy split --disable_benign false

# generate all (benign + attack, all in one)
sudo bash start-log.sh --n_benign 10 --n_attack 1 --total_time 2 --data_attack_type modify --graph_strategy all --disable_benign false
