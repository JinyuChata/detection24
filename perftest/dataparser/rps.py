import sys, os


def parse_rps(filepath):
    alls = []
    for filename in os.listdir(filepath):
        if "testperf-" not in filename:
            continue
        fp = filepath + "/" + filename
        ffn = filename.replace("testperf-worker", "")
        ffn = ffn.replace("reqpersec", "")
        ffn = ffn.replace(".txt", "")
        worker_cnt, rps = ffn.split(".")
        worker_cnt = int(worker_cnt)
        rps = int(rps)
        rps = rps * worker_cnt
        with open(fp, "r") as f:
            for line in f:
                if "Average:" not in line:
                    continue
                line = line.replace("Average:", "")
                line = line.replace("secs", "")
                line = line.replace("\n", "")
                line = line.strip()
                alls.append((rps, float(line)))
    alls = sorted(alls, key=lambda x: x[0])
    return alls


if __name__ == "__main__":
    filepaths = ["../result-alastor", "../result-vanilla"]
    res = []
    for fpss in filepaths:
        res.append(parse_rps(fpss))
    print(",".join(filepaths))
    for i in range(len(res[0])):
        talls = []
        for j in range(len(filepaths)):
            talls.append(str(res[j][i][1]))
        print(",".join([str(res[0][i][0])] + talls))
