## Prepare MySQL



## Start

```bash
bash start-log.sh --n_benign 10 --n_attack 5 --total_time 5 --data_attack_type leak
```

## Notes

```bash
go run main.go graph ../output/leak-20240625230313/sysdig/5de98637-66c0-4ed6-bbb0-09050b2cfd0e.log ../output/leak-20240625230313/net/5de98637-66c0-4ed6-bbb0-09050b2cfd0e.log remove_all
go run main.go dot ../output/leak-20240625230313/outputa.dot
python3.9 generate-dot.py ./output/leak-20240625230313
```