import os

def split_txt_file(file_path, n, pa):
    with open(file_path, 'r', encoding='utf-8') as original_file:
        content = original_file.read()
        lines = content.split('\n')
        total_lines = len(lines)
        lines_per_file = total_lines // n
        tmp = file_path.split('/')[2].split('.')[0]
        start = 0
        for i in range(n):
            end = start + lines_per_file
            if i == n - 1:
                end = total_lines

            sub_content = '\n'.join(lines[start:end])
            new_file_name = f'{tmp}_{i + 1}.txt'
            ff = os.path.join(pa, new_file_name)
            with open(ff, 'w', encoding='utf-8') as sub_file:
                sub_file.write(sub_content)
            start = end

# file_path = 'your_original_file.txt'
# n = 3  # 分成 3 份，可以根据实际情况修改
# split_txt_file(file_path, n)

folder_1 = './data_train_alastor'
folder_2 = './data_test_alastor'
train_data_list = [os.path.join(folder_1, f) for f in os.listdir(folder_1) if f.endswith('.log') and 'rc3' in f]
test_data_list = [os.path.join(folder_2, f) for f in os.listdir(folder_2) if f.endswith('.log') and 'rc3' in f]
for pa in train_data_list:
    split_txt_file(pa,5,'./split_train')
for pa in test_data_list:
    split_txt_file(pa,2,'./split_test')


print()
