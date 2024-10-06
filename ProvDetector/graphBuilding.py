import numpy as np
from Graph import *
import pymysql


def search_node(id_, cursor):
    # 查询
    query_file = "SELECT * FROM file WHERE id = %s"
    query_process = "SELECT * FROM process WHERE id = %s"
    query_socket = "SELECT * FROM socket WHERE id = %s"
    
    cursor.execute(query_file, id_)
    re1 = cursor.fetchall()
    if re1 != ():
        # print(re1)
        return re1[0][-1], "file"

    cursor.execute(query_process, id_)
    re2 = cursor.fetchall()   
    if re2 != ():
        # print(re2[0][-1])
        return re2[0][-1], "process"
    
    cursor.execute(query_socket, id_)
    re3 = cursor.fetchall()   
    if re3 != ():
        # print(re3)
        return re3[0][5]+':'+re3[0][6], "socket"
     
    print("id_ NOT Found!")
    return "", ""


def graphBuilding(db_list):
    G = []
    for each in db_list: # path_list可以变为数据库名称的list！！！
        G_now = Graph()
        cnt = 0
        line_now = []

        # MySQL数据库连接配置信息
        connection = pymysql.connect(
            host='localhost',        # 数据库主机
            port=3307,
            user='root',     # 数据库用户名
            password='Erinyes@2024', # 数据库密码
            database=each  # 要连接的数据库名称
        )

        try:
            print("============================Start graph-building of db: " + each + "============================")
            # 创建一个游标对象
            with connection.cursor() as cursor:
                # 执行SQL查询
                query = "SELECT * FROM event"
                cursor.execute(query)

                # 获取所有结果
                results = cursor.fetchall()
                for row in results:
                    # row[1],row[2],row[5],row[6] ----- src_-d, dst_id, operation, timestamp
                    # 需要去file/process/socket表里查找row[1]和row[2]
                    re_src, type_src = search_node(row[1], cursor=cursor)
                    re_dst, type_dst = search_node(row[2], cursor=cursor)
                    # print(re_src)
                    # print(type_src)
                    temp = [re_src] + [type_src] + [re_dst] + [type_dst] + [row[5]] + [row[6]]
                    line_now.append(temp)
                    print(temp)

        finally:
            # 关闭连接
            connection.close()



################################################################################        

        # f_now = open(i, 'r', encoding='utf-8')
        # ts_now = []
        # for line in f_now:
        #     line_now.append(line)
        #     ts_now.append(float(line.strip('\n').split('\t')[5]))
        # sorted_index = np.argsort(ts_now, axis=0)
        # line_now = np.array(line_now)[sorted_index]

        for line in line_now:  # srcId srcType dstId dstType edgeType timestamp
            # line = line.strip('\n').split('\t')
            temp = float(line[5])
            if G_now.min_ts < 0: G_now.min_ts = temp
            if G_now.max_ts < 0: G_now.max_ts = temp
            if temp < G_now.min_ts: G_now.min_ts = temp
            if temp > G_now.max_ts: G_now.max_ts = temp

            if not line[0] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[0]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[0]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[0]] = 1
                G_now.node_cnt += 1
            if not line[2] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1
            if G_now.flag[line[2]] == 1:
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1

            G_now.flag[line[0]] = 1  # 修改，避免环路问题

            G_now.nodeType_map[G_now.nodeId_map[line[0]]] = line[1]
            G_now.nodeType_map[G_now.nodeId_map[line[2]]] = line[3]
            G_now.out_edges[G_now.nodeId_map[line[0]]].append(G_now.edge_cnt)
            G_now.in_edges[G_now.nodeId_map[line[2]]].append(G_now.edge_cnt)
            G_now.e_src.append(G_now.nodeId_map[line[0]])
            G_now.e_dst.append(G_now.nodeId_map[line[2]])
            G_now.e_type.append(line[4])
            G_now.e_ts.append(float(line[5]))
            G_now.edge_cnt += 1

        G_now.nodeType_map[G_now.node_cnt] = 'start'
        G_now.nodeId_map['Start_node'] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = 'Start_node'
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        G_now.nodeType_map[G_now.node_cnt] = 'end'
        G_now.nodeId_map['End_node'] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = 'End_node'
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        for j in range(G_now.node_cnt - 2):
            if len(G_now.in_edges[j]) == 0:
                G_now.out_edges[G_now.node_cnt - 2].append(G_now.edge_cnt)
                G_now.in_edges[j].append(G_now.edge_cnt)
                G_now.e_src.append(G_now.node_cnt - 2)
                G_now.e_dst.append(j)
                G_now.e_type.append('start_edge')
                G_now.e_ts.append(max(G_now.min_ts - 100, 0))
                G_now.edge_cnt += 1

            if len(G_now.out_edges[j]) == 0:
                G_now.out_edges[j].append(G_now.edge_cnt)
                G_now.in_edges[G_now.node_cnt - 1].append(G_now.edge_cnt)
                G_now.e_src.append(j)
                G_now.e_dst.append(G_now.node_cnt - 1)
                G_now.e_type.append('end_edge')
                G_now.e_ts.append(G_now.min_ts + 100)
                G_now.edge_cnt += 1

        G.append(G_now)
    return G
