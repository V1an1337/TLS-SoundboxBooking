import mysql.connector
from datetime import datetime, timedelta

# MySQL连接配置
config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
    'database': 'SoundboxBooking',
}

# 创建数据库连接
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# 当前日期和未来四天的日期
dates = [datetime.now().date() + timedelta(days=i) for i in range(5)]

# 插入数据
for date in dates:
    for id in range(1, 61):
        for block in range(1, 11):
                sql = "INSERT INTO Booking (id, date, block, status, bookBy) VALUES (%s, %s, %s, %s, %s)"
                values = (id, date, block, False, None)  # bookBy 设置为 None
                cursor.execute(sql, values)

# 提交事务
conn.commit()

# 关闭连接
cursor.close()
conn.close()

print("数据插入完成！")
