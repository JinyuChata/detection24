import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 14  # 设置字体大小为12

# 读取三个 CSV 文件
csv_file1 = './result-vanilla.csv'
csv_file2 = './result-alastor.csv'
csv_file3 = './result-erinyes.csv'

df1 = pd.read_csv(csv_file1)
df2 = pd.read_csv(csv_file2)
df3 = pd.read_csv(csv_file3)

# 选择需要的列，假设这三个文件有相同的列名
selected_columns = ['HostMem']
df1_selected = df1[selected_columns]
df2_selected = df2[selected_columns]
df3_selected = df3[selected_columns]

df1_hostcpu = df1['HostCPU']
df2_hostcpu = df2['HostCPU']
df3_hostcpu = df3['HostCPU']

df1_containercpu = df1['NodeCPU']
df2_containercpu = df2['NodeCPU']
df3_containercpu = df3['NodeCPU']

df1_containermem = df1['NodeMEM']
df2_containermem = df2['NodeMEM']
df3_containermem = df3['NodeMEM']

# 合并三个 DataFrame
merged_df = pd.concat([df1_selected, df2_selected, df3_selected], axis=1)
merged_df_hostcpu = pd.concat([df1_hostcpu, df2_hostcpu, df3_hostcpu], axis=1)
merged_df_nodecpu = pd.concat([df1_containercpu, df2_containercpu, df3_containercpu], axis=1)
merged_df_nodemem = pd.concat([df1_containermem, df2_containermem, df3_containermem], axis=1)

new_column_names = ['vanilla', 'alastor', 'eirnyes']
merged_df.columns = new_column_names
merged_df_hostcpu.columns = new_column_names
merged_df_nodecpu.columns = new_column_names
merged_df_nodemem.columns = new_column_names
# print(merged_df.columns)


# 写入新的 CSV 文件
merged_csv_file = 'merged_data.csv'
merged_df.to_csv(merged_csv_file, index=False)

# print(merged_df['HostMem'])
rps_list = [1,5,10,20,50,100]
rps_list = [x * 5 for x in rps_list for _ in range(3)]
time_list = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150]
rps_list = rps_list[:len(time_list)]  # TODO: rps_list 添加第二条x轴 (在上方)

rps_disp, time_disp = [], []
last_rps = -1
for i in range(len(time_list)):
    if last_rps != rps_list[i]:
        last_rps = rps_list[i]
        rps_disp.append(last_rps)
        time_disp.append(time_list[i])

print(rps_disp, len(rps_disp))
print(time_disp, len(time_disp))
rps_disp[-1] = "Req/s"

# 生成折线图
fig = plt.figure(figsize=(14, 8), dpi=150)

def show_in(x, y, z, df, sci=False, scibase=6, scibasemath=1e6, x_label="Time[s]", y_label="", title="", frac=1):
    plt.subplot(x, y, z)
    # plt.figure(figsize=(8, 6), dpi=150)
    plt.plot(time_list, df['vanilla'], 'tab:green', label='Vanilla')
    plt.plot(time_list, df['alastor'], 'tab:blue', label='Alastor')
    plt.plot(time_list, df['eirnyes'], 'tab:red', label='Erinyes')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    ax1 = plt.gca()
    if sci:
        def formatnum(x, pos):
            return '%.FRACf×10$^{BASE}$'.replace("BASE", str(scibase)).replace("FRAC", str(frac)) % (x / scibasemath)
        formatter = FuncFormatter(formatnum)
        ax1.yaxis.set_major_formatter(formatter)
    ax1.tick_params(axis='x', direction='in')  # 第一个x轴刻度朝内
    ax1.tick_params(axis='y', direction='in')  # 第一个y轴刻度朝内
    ax1.xaxis.set_label_coords(.98, -.016)
    ax2 = ax1.twiny()
    ax2.set_xticks(time_disp)
    ax2.set_xticklabels(rps_disp)
    # ax2.set_xlabel('Request Per Second')
    ax2.xaxis.tick_top()
    ax2.xaxis.set_label_position('top')
    ax2.tick_params(axis='x', direction='in')  # 将坐标轴Tick朝内
    plt.title(title, loc="center", fontdict={'fontsize': 18, 'fontname': 'Times New Roman'}, pad=15)

show_in(2, 2, 1, merged_df, sci=True, scibase=6, scibasemath=1e6, y_label="Memory [MB]", title="(a) Host memory utilization")
show_in(2, 2, 2, merged_df_nodemem, sci=True, scibase=7, scibasemath=1e7, frac=2, y_label="Memory [MB]", title="(b) Function memory utilization")
show_in(2, 2, 3, merged_df_hostcpu, y_label="Percent [%]", title="(c) Host CPU utilization")
show_in(2, 2, 4, merged_df_nodecpu, sci=True, scibase=9, scibasemath=1e9, y_label="nanoCPU", title="(d) Function CPU utilization")


plt.tight_layout()
plt.savefig('perf.pdf', bbox_inches='tight')
plt.show()

# 或者保存为图片文件
# plt.savefig('line_chart.pdf')
