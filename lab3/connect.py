import pyodbc

# 连接到 MySQL 数据库
conn_str = 'DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=localhost:3306;DATABASE=db_lab3;UID=root;PWD=nwj_ustc;'
conn = pyodbc.connect(conn_str)

# 创建游标
cursor = conn.cursor()

# 执行查询语句
cursor.execute("SELECT * FROM course")

# 获取查询结果
rows = cursor.fetchall()
print(rows)

# 遍历结果
for row in rows:
    print(row)

# 关闭游标和连接
cursor.close()
conn.close()
