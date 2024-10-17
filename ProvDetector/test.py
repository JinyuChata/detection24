import os
folder_1 = '/home/ubuntu/detection24/log-collection/output-train'
train_list = [f.path for f in os.scandir(folder_1) if f.is_dir() and 'rc3' in f.path]
for f in train_list:
    print("-----------========-----------" + f)
    pa = os.path.join(f, "sysdig")
    for i in os.listdir(pa):
        if "sysdig" in i:
            continue
        full_path = os.path.join(pa, i)
        print(full_path)
        # train_data_list.append(full_path)
