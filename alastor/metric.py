import networkx as nx
import re
import os
import statistics
import argparse
import pydot

def merge_dot_files(dot_files, output_file):
    # 创建一个空的总图
    merged_graph = pydot.Dot(graph_type="digraph")

    # 遍历所有的dot文件
    for dt in dot_files:
        # 读取当前dot文件
        graphs = pydot.graph_from_dot_file(dt)
        for graph in graphs:
            for node in graph.get_nodes():
                merged_graph.add_node(node)
            for edge in graph.get_edges():
                merged_graph.add_edge(edge)

    # 将合并后的图保存为新的dot文件
    merged_graph.write(output_file, format="raw")


def load_graph(file_path):
    """从.dot文件加载图"""
    return nx.drawing.nx_pydot.read_dot(file_path)

def replace_node_label(node_label):
    node_label = re.sub(r'Process##\d+', 'Process##PID', node_label)
    node_label = re.sub(r':\d{5}', ':RD_PORT', node_label)
    return node_label



# def calculate_all(gt_graph, sample_graph):
#     gt_nodes = set(list(map(lambda x: replace_node_label(x), gt_graph.nodes())))
#     sample_nodes = set(list(map(lambda x: replace_node_label(x), sample_graph.nodes())))
    
#     gt_edges = set(list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), gt_graph.edges())))
#     sample_edges = set(list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), sample_graph.edges())))
#     node_accuracy = calc(gt_nodes, sample_nodes)
#     edge_accuracy = calc(gt_edges, sample_edges)
#     return {'node': node_accuracy, 'edge': edge_accuracy}

# def calc(gt, sample):
#     TP = len(gt & sample)
#     FP = len(sample - gt)
#     FN = len(gt - sample)
    
#     accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0
#     precision = TP / (TP + FP) if (TP + FP) > 0 else 0
#     recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    
#     return TP, FP, FN, accuracy * 100, precision * 100, recall * 100

from collections import Counter

def calculate_all(gt_graph, sample_graph):
    gt_nodes = list(map(lambda x: replace_node_label(x), gt_graph.nodes()))
    sample_nodes = list(map(lambda x: replace_node_label(x), sample_graph.nodes()))
    
    gt_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), gt_graph.edges()))
    sample_edges = list(map(lambda x: replace_node_label(x[0]) + " => " + replace_node_label(x[1]), sample_graph.edges()))

    node_accuracy = calc(gt_nodes, sample_nodes, "node")
    edge_accuracy = calc(gt_edges, sample_edges, 'edge')
    
    return {'node': node_accuracy, 'edge': edge_accuracy}

def calc(gt, sample, info):
    gt_count = Counter(gt)
    sample_count = Counter(sample)

    TP = sum(min(gt_count[node], sample_count[node]) for node in sample_count)
    FP = sum(sample_count[node] for node in sample_count) - TP
    FN = sum(gt_count[node] for node in gt_count) - TP
    
    print(f"benign {info}: {FP}")

    # Adjust FN based on the count
    FN = sum(gt_count[node] - min(gt_count[node], sample_count[node]) for node in gt_count)

    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    
    return TP, FP, FN, accuracy * 100, precision * 100, recall * 100



def metric_main(info, gt_file, sample_path):
    edge_accuracies = []
    node_accuracies = []
    
    gt_graph = load_graph(gt_file)
    sample_graph = load_graph(sample_path)
    
    print(f"attack nodes: {len(gt_graph.nodes())}, edges: {len(gt_graph.edges())}")
    print(f"sample nodes: {len(sample_graph.nodes())}, edges: {len(sample_graph.edges())}")
    
    alls = calculate_all(gt_graph, sample_graph)
    n_tp, n_fp, n_fn, n_acc, n_pre, n_recall = alls['node']
    e_tp, e_fp, e_fn, e_acc, e_pre, e_recall = alls['edge']
    
    # print(f"{info}, Node: Pre {n_pre:.2f}, Recall {n_recall:.2f}, TP {n_tp}, FP {n_fp}, FN {n_fn}")
    print(f"{info}, Edge: Pre {e_pre:.2f}, Recall {e_recall:.2f}, TP {e_tp}, FP {e_fp}, FN {e_fn}")
    print()
    
def find_latest_timestamped_directory(base_dir, attack_type='modify', file_type='gt'):
    max_timestamp = -1
    latest_dir = None

    # 遍历base_dir目录下的所有子目录
    for entry in os.listdir(base_dir):
        if entry.startswith(f"{attack_type}-{file_type}-"):
            # 提取时间戳
            match = re.search(rf"{attack_type}-{file_type}-(\d+)", entry)
            if match:
                timestamp = int(match.group(1))
                if timestamp > max_timestamp:
                    max_timestamp = timestamp
                    latest_dir = entry

    return os.path.join(base_dir, latest_dir)

def find_dot_file(base_dir):
    dot_file_path = None
    dot_attack_dir = os.path.join(base_dir, 'dot')
    dot_attack_dir_all = os.path.join(base_dir, 'dot', "all.dot")
    
    dots = []
    if os.path.exists(dot_attack_dir):
        for entry in os.listdir(dot_attack_dir):
            if entry.endswith('.dot') and not entry.startswith("all"):
                dot_file_path = os.path.join(dot_attack_dir, entry)
                dots.append(dot_file_path)
    merge_dot_files(dots, dot_attack_dir_all)
    return dot_attack_dir_all


if __name__ == "__main__":
    # attacks = ['modify', 'leak', 'warm', 'cfattack']
    attacks = ['escape', 'cfattack']
    for attack in attacks:
        gt_base = find_latest_timestamped_directory("./output", attack_type=attack, file_type='gt')
        rc1_base = find_latest_timestamped_directory("./output", attack_type=attack, file_type='rc1')
        rc2_base = find_latest_timestamped_directory("./output", attack_type=attack, file_type='rc2')
        rc3_base = find_latest_timestamped_directory("./output", attack_type=attack, file_type='rc3')
        gt, rc1, rc2, rc3 = find_dot_file(gt_base), find_dot_file(rc1_base), find_dot_file(rc2_base), find_dot_file(rc3_base)
        print(f"===== {attack} =====")
        metric_main("rc1", gt, rc1)
        metric_main("rc2", gt, rc2)
        metric_main("rc3", gt, rc3)
