# -*- coding: utf-8 -*-
import networkx as nx  # 导入NetworkX库，用于处理图结构
import re  # 导入正则表达式模块，用于字符串模式匹配和替换
import os  # 导入操作系统模块，用于文件和目录操作
import statistics  # 导入统计模块，用于统计数据计算
import argparse  # 导入命令行参数解析模块，用于接收用户输入的参数


def load_graph(file_path):  # 定义一个函数从.dot文件加载图
    """从.dot文件加载图"""
    return nx.drawing.nx_pydot.read_dot(file_path)  # 使用NetworkX中的read_dot函数解析.dot文件并返回图对象


def replace_node_label(node_label):  # 定义一个函数，用于替换节点标签中的特定模式
    node_label = re.sub(r'\[\d+\]', '[RD_ID]', node_label)  # 将"[数字]"模式替换为"[RD_ID]"
    node_label = re.sub(r'\b\d+_', 'PID_', node_label)  # 将以数字开头的"数字_"模式替换为"PID_"
    node_label = re.sub(r'_[a-f0-9]{12}', '_UUID', node_label)  # 将下划线后跟12个十六进制字符的模式替换为"_UUID"
    node_label = re.sub(r':\d{5}', ':RD_PORT', node_label)  # 将五位数字端口替换为":RD_PORT"
    node_label = re.sub(r':\d{4}', ':RD_PORT', node_label)  # 将四位数字端口替换为":RD_PORT"
    node_label = re.sub(r':\d{3}', ':RD_PORT', node_label)  # 将三位数字端口替换为":RD_PORT"
    node_label = re.sub(r':\d{2}', ':RD_PORT', node_label)  # 将两位数字端口替换为":RD_PORT"
    node_label = re.sub(r'[\d\.]+:', 'RD_IP:', node_label)  # 将IP地址形式（数字和点组合）替换为"RD_IP:"
    node_label = re.sub(r'_.{10}-.{5}', '_UUID', node_label)  # 将"_10字符-5字符"模式替换为"_UUID"
    return node_label  # 返回替换后的节点标签


from collections import Counter  # 从collections模块导入Counter，用于统计元素出现次数


def calculate_all(gt_graph, sample_graph):  # 定义一个函数，计算样本图和真实图的节点和边匹配情况
    gt_nodes = list(map(lambda x: replace_node_label(x), gt_graph.nodes()))  # 替换真实图中节点的标签
    sample_nodes = list(map(lambda x: replace_node_label(x), sample_graph.nodes()))  # 替换样本图中节点的标签
    gt_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), gt_graph.edges()))  # 替换真实图中边的标签
    sample_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), sample_graph.edges()))  # 替换样本图中边的标签
    
    gt_edges = list(set(gt_edges))  # 去重真实图中的边
    gt_nodes = list(set(gt_nodes))  # 去重真实图中的节点
    sample_edges = list(set(sample_edges))  # 去重样本图中的边
    sample_nodes = list(set(sample_nodes))  # 去重样本图中的节点

    print(f"attack nodes: {len(gt_nodes)}, edges: {len(gt_edges)}")  # 打印真实图中节点和边的数量
    print(f"sample nodes: {len(sample_nodes)}, edges: {len(sample_edges)}")  # 打印样本图中节点和边的数量

    print("in attack but not in sample: ")  # 打印存在于真实图中但不在样本图中的边
    for attack_edge in gt_edges:  # 遍历真实图中的边
        if attack_edge not in sample_edges:  # 如果该边不在样本图中
            print(f"--- {attack_edge}")  # 输出该边

    node_accuracy = calc(gt_nodes, sample_nodes, "node")  # 计算节点的准确性
    edge_accuracy = calc(gt_edges, sample_edges, 'edge')  # 计算边的准确性
    
    return {'node': node_accuracy, 'edge': edge_accuracy}  # 返回节点和边的准确性结果


def calc(gt, sample, info):  # 定义一个函数，计算TP（真阳性）、FP（假阳性）、FN（假阴性）及准确性指标
    gt_count = Counter(gt)  # 统计真实数据中每个元素的出现次数
    sample_count = Counter(sample)  # 统计样本数据中每个元素的出现次数
    TP = sum(min(gt_count[node], sample_count[node]) for node in gt_count)  # 计算真阳性：两者都存在的最小出现次数之和
    FP = sum(sample_count.values()) - TP  # 计算假阳性：样本中独有的数量
    FN = sum(gt_count.values()) - TP  # 计算假阴性：真实数据中独有的数量

    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0  # 计算准确率
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0  # 计算精确率
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0  # 计算召回率
    
    return TP, FP, FN, accuracy * 100, precision * 100, recall * 100  # 返回计算结果


# 主函数和其他辅助函数的注释内容省略，如需详细注释后续代码请告知。
def metric_main(info, gt_file, sample_path):  # 定义一个函数，用于评估图的节点和边的匹配情况
    edge_accuracies = []  # 初始化一个列表，用于存储边的准确性
    node_accuracies = []  # 初始化一个列表，用于存储节点的准确性
    
    gt_graph = load_graph(gt_file)  # 加载真实图文件
    sample_graph = load_graph(sample_path)  # 加载样本图文件
    
    alls = calculate_all(gt_graph, sample_graph)  # 计算样本图与真实图的节点和边匹配结果
    n_tp, n_fp, n_fn, n_acc, n_pre, n_recall = alls['node']  # 获取节点匹配的评估指标
    e_tp, e_fp, e_fn, e_acc, e_pre, e_recall = alls['edge']  # 获取边匹配的评估指标
    
    print(f"{info}, Edge: Pre {e_pre:.2f}, Recall {e_recall:.2f}, TP {e_tp}, FP {e_fp}, FN {e_fn}")  # 打印边匹配的评估结果


def metric_benign(gt, sample, name):  # 定义一个函数，用于计算样本中多余的节点或边数量
    gt_count = Counter(gt)  # 统计真实数据中每个元素的出现次数
    sample_count = Counter(sample)  # 统计样本数据中每个元素的出现次数
    remaining_count = sample_count - gt_count  # 计算样本中多余的元素
    remaining_total = sum(remaining_count.values())  # 求出多余元素的总数量
    print(f"BENIGN {name}: {remaining_total}")  # 打印多余元素的总数量


def metric_main_alls(gt_file, sample_path):  # 定义一个函数，用于评估节点和边的多余元素
    gt_graph = load_graph(gt_file)  # 加载真实图文件
    sample_graph = load_graph(sample_path)  # 加载样本图文件
    gt_nodes = list(map(lambda x: replace_node_label(x), gt_graph.nodes()))  # 替换真实图中节点的标签
    sample_nodes = list(map(lambda x: replace_node_label(x), sample_graph.nodes()))  # 替换样本图中节点的标签
    gt_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), gt_graph.edges()))  # 替换真实图中边的标签
    sample_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), sample_graph.edges()))  # 替换样本图中边的标签
    
    metric_benign(gt_nodes, sample_nodes, "nodes")  # 计算并打印节点中多余元素的数量
    metric_benign(gt_edges, sample_edges, "edges")  # 计算并打印边中多余元素的数量


def find_latest_timestamped_directory(base_dir, attack_type='modify', file_type='gt'):  # 查找目录中时间戳最新的子目录
    max_timestamp = -1  # 初始化最大时间戳
    latest_dir = None  # 初始化最新目录

    for entry in os.listdir(base_dir):  # 遍历目录中的所有子目录
        if entry.startswith(f"{attack_type}-{file_type}-"):  # 筛选符合指定类型和文件类型的目录
            match = re.search(rf"{attack_type}-{file_type}-(\d+)", entry)  # 使用正则表达式提取时间戳
            if match:  # 如果匹配成功
                timestamp = int(match.group(1))  # 将时间戳转为整数
                if timestamp > max_timestamp:  # 如果当前时间戳比记录的最大时间戳更大
                    max_timestamp = timestamp  # 更新最大时间戳
                    latest_dir = entry  # 更新最新目录
    return os.path.join(base_dir, latest_dir)  # 返回最新目录的完整路径


def find_dot_file(base_dir):  # 查找目录中第一个以.dot结尾的文件
    dot_file_path = None  # 初始化.dot文件路径
    dot_attack_dir = os.path.join(base_dir, 'dot', 'attack')  # 构造目标路径
    
    if os.path.exists(dot_attack_dir):  # 如果目标路径存在
        for entry in os.listdir(dot_attack_dir):  # 遍历目标路径中的所有文件
            if entry.endswith('.dot'):  # 如果文件以.dot结尾
                dot_file_path = os.path.join(dot_attack_dir, entry)  # 获取文件完整路径
                break  # 找到第一个文件后退出循环

    return dot_file_path  # 返回找到的文件路径


def find_all_dot_file(base_dir):  # 查找目录中第一个以all.dot结尾的文件
    dot_file_path = None  # 初始化.all.dot文件路径
    dot_attack_dir = os.path.join(base_dir, 'dot')  # 构造目标路径
    
    if os.path.exists(dot_attack_dir):  # 如果目标路径存在
        for entry in os.listdir(dot_attack_dir):  # 遍历目标路径中的所有文件
            if entry.endswith('all.dot'):  # 如果文件以all.dot结尾
                dot_file_path = os.path.join(dot_attack_dir, entry)  # 获取文件完整路径
                break  # 找到第一个文件后退出循环

    return dot_file_path  # 返回找到的文件路径


if __name__ == "__main__":  # 主函数入口
    attacks = ['cfattack', 'escape']  # 定义攻击类型列表
# 遍历每种攻击类型
    for attack in attacks:  
        gt_base = find_latest_timestamped_directory("/home/ubuntu/detection24/log-collection/output-ysl-1115", attack_type=attack, file_type='gt')  # 获取真实图的最新目录
        rc1_base = find_latest_timestamped_directory("/home/ubuntu/detection24/log-collection/output-ysl-1115", attack_type=attack, file_type='rc1')  # 获取样本1的最新目录
        rc2_base = find_latest_timestamped_directory("/home/ubuntu/detection24/log-collection/output-ysl-1115", attack_type=attack, file_type='rc2')  # 获取样本2的最新目录
        rc3_base = find_latest_timestamped_directory("/home/ubuntu/detection24/log-collection/output-ysl-1115", attack_type=attack, file_type='rc3')  # 获取样本3的最新目录
        print(gt_base)  # 打印真实图目录路径

        # 获取真实图和样本图的.dot文件路径
        gt, rc1, rc2, rc3 = find_dot_file(gt_base), find_dot_file(rc1_base), find_dot_file(rc2_base), find_dot_file(rc3_base)
        gt_all, rc1_all, rc2_all, rc3_all = find_all_dot_file(gt_base), find_all_dot_file(rc1_base), find_all_dot_file(rc2_base), find_all_dot_file(rc3_base)
        
        print(f"===== {attack} =====")  # 打印攻击类型分隔线
        metric_main("rc1", gt, rc1)  # 评估真实图和样本1的匹配
        metric_main_alls(gt, rc1_all)  # 评估真实图和样本1的多余元素
        
        metric_main("rc2", gt, rc2)  # 评估真实图和样本2的匹配
        metric_main_alls(gt, rc2_all)  # 评估真实图和样本2的多余元素
        
        metric_main("rc3", gt, rc3)  # 评估真实图和样本3的匹配
        metric_main_alls(gt, rc3_all)  # 评估真实图和样本3的多余元素
