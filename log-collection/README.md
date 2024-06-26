## Introduction

`log-collection` contains the following functions:

1. Send benign and attack requests with random uuid concurrently
2. Collect sysdig log
3. Collect network log
4. Dispatch log by type (attack or benign) and uuid
5. Generate request-level graph based on log (dot & svg)

## Start

```bash
bash start-log.sh --n_benign 10 --n_attack 5 --total_time 5 --data_attack_type leak
```

### Arguments

`start-log.sh` will send `n_benign` of benign requests as well as `n_attack` of attack requests in `total_time` seconds, and the attack type is `data_attack_type`.

### Attack type: data_attack_type

- `leak`: leakage of crenditials
- `modify`: command injection resulted in file modification