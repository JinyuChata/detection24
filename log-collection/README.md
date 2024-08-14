## Introduction

`log-collection` contains the following functions:

1. Auto generate configurations for erinyes via `kubectl get pods` and `kubectl get svc`
2. Send benign and attack requests with random uuid concurrently
3. Collect sysdig log
4. Collect network log
5. Dispatch log by type (attack or benign) and uuid
6. Generate request-level graph based on log (dot & svg)

## Start

```bash
bash start-log.sh --n_benign 10 --n_attack 5 --total_time 5 --data_attack_type leak --graph_strategy split
bash start-log.sh --n_benign 10 --n_attack 5 --total_time 5 --data_attack_type leak --graph_strategy all 

bash start-log.sh --n_benign 0 --n_attack 1 --total_time 1 --data_attack_type warm1 --graph_strategy all
bash start-log.sh --n_benign 0 --n_attack 1 --total_time 1 --data_attack_type warm2 --graph_strategy all
```

Script outputs will be stored in `./output/ATTACKTYPE-ACTIONTIME`, 

### Arguments

`start-log.sh` will send `n_benign` of benign requests as well as `n_attack` of attack requests in `total_time` seconds, and the attack type is `data_attack_type`.

### Attack type: data_attack_type

- `leak`: leakage of crenditials
- `modify`: command injection resulted in file modification
- `warm1`, `warm2`: warm container reuse in alastor

### Split graph by request uuid: graph_strategy

- `split`: split graph by req uuid
- `all`: contain a large, unsplit graph