import os
import re

# parent_folder = './output-train'
parent_folder = './output-test'

subfolders = [f.path for f in os.scandir(parent_folder) if f.is_dir()]

for subfolder in subfolders:
    print(subfolder)
    ss = subfolder.split('/')[-1] + ".log"
    txtp = os.path.join("/home/ubuntu/detection24/ProvDetector/data_test_alastor", ss)
    # txtp = os.path.join("/home/ubuntu/detection24/ProvDetector/data_train_alastor", ss)
    print(txtp)
    res = []
    pa = os.path.join(subfolder, "raw")
    final_pa = [f.path for f in os.scandir(pa) if f.is_dir()]
    for p in final_pa:
        # print(p)
        for filename in os.listdir(p):
            if filename != "request.alastor.log":
                file_path = os.path.join(p, filename)
                # print(file_path)
                try:
                    with open(file_path, 'r') as file:
                        content = file.readlines()
                        pro_id = file_path[-2:] # process id

                        for line in content:
                            # print(line)
                            index = line.find("(")
                            # print(line[18:index]) # operation
                            pattern_t = r'\d+\.\d+'
                            match_t = re.match(pattern_t, line)


                            i1 = line[index:-1].find("\"")
                            if i1==-1:
                                continue
                            i2 = line[index+i1+1:-1].find("\"")
                            obj = line[index+i1+1:index+i1+i2+1]
                            # print(line[index+i1+1:index+i1+i2+1]) # object                             

                            tmp = []
                            tmp.append(pro_id)
                            tmp.append("process")                     
                            tmp.append(obj)
                            if obj.find("\\") != -1 or obj.find("/") != -1:
                                tmp.append("file")
                            else:
                                tmp.append("socket")
                            tmp.append(line[18:index])     
                            tmp.append(str(int(float(match_t[0])*1000)))
                            # print(tmp)
                            res.append(tmp)
                  
                except FileNotFoundError:
                    print(f'文件 {filename} 不存在')
                # except Exception as e:
                #     print(f'读取文件 {filename} 时出现错误：{e}')
    sorted_res = sorted(res, key=lambda x: float(x[-1]))
    # for i in sorted_res:
    #     print(i)
    # print("---------------")
    try:
        with open(txtp, 'w') as file:
            for row in sorted_res:
                line = '\t'.join(row) + '\n'
                file.write(line)
    except FileNotFoundError:
        print("文件不存在，无法写入")
    # break
