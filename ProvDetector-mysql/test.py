import numpy as np
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


def graphBuilding(path_list):
    G = []
    for each in path_list:
        # G_now = Graph()
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
            # 创建一个游标对象
            with connection.cursor() as cursor:
                # print("aaaaaaaaaaaaaaaaaaaaa")
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



if __name__ == '__main__':
    a=["erinyes_a_cf",]
    graphBuilding(a)
