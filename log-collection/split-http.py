import json
import os
import argparse  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process net.log and write UUID-specific logs.")  
    parser.add_argument("--dir", "-d", required=True, help="Output directory to store UUID log files")  
    args = parser.parse_args()  

    # 获取传入的目录参数  
    di = args.dir 
    d = f"{di}/net"
    with open(f"{d}/net.log", 'r') as f:
        s = set()
        for line in f.readlines():
            if "uuid:" in line:
                obj = json.loads(line)
                ls = obj['payload'].split('\r\n')
                for l in ls:
                    if "uuid:" in l:
                        uuid = l.split(': ')[1]
                        s.add(uuid)
                        output_file = os.path.join(d, f"{uuid}.log")  
                        with open(output_file, 'a') as out_file:  
                            out_file.write(line) 