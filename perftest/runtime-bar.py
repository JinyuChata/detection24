import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import StrMethodFormatter

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 14  # 设置字体大小为12
# 三个系列的数据

# vanilla = [0.007, 0.007, 0.007, 0.015, 0.13]
# alastor = [0.008, 0.007, 0.007, 0.017, 0.13]
# erinyes = [0.008, 0.008, 0.007, 0.016, 0.13]

vanilla = [0.007, 0.009, 0.007, 0.007, 0.739]
alastor = [0.009, 0.013, 0.010, 0.010, 1.257]
erinyes = [0.008, 0.009, 0.008, 0.008, 0.761]
labels = [
    'purchase', 'info-modify', 'info-leak', 'file-download', 'sentiment-analysis'
]

# 计算每个系列的柱状图中心位置
x = [i for i in range(len(vanilla))]
fig = plt.figure(figsize=(8, 5), dpi=150)

# 绘制柱状图
plt.bar([i - 0.16 for i in x], vanilla, color='tab:green', width=0.16, align='center', label='Vanilla', edgecolor='black', linewidth=1.5)
plt.bar(x, erinyes, color='tab:red', width=0.16, align='center', label='Erinyes', edgecolor='black', linewidth=1.5)
plt.bar([i + 0.16 for i in x], alastor, color='tab:blue', width=0.16, align='center', label='Alastor', edgecolor='black', linewidth=1.5)

# 添加标签、标题和图例
plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:.3f}'))  # 设置 y 轴刻度格式为保留 3 位小数
plt.ylabel('Response Time [s]')
plt.legend()

# 设置 X 轴的刻度位置和标签
plt.xticks(x, labels, rotation=350)

# 显示图形
plt.tight_layout()
plt.savefig('resp.pdf', bbox_inches='tight')

plt.show()
