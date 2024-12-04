import mysql.connector
from mysql.connector import errorcode

# MySQL连接配置
config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
}

# 连接到MySQL
try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS SoundboxBooking")
    cursor.execute("USE SoundboxBooking")

    # 删除User表（如果存在），然后创建User表
    cursor.execute("DROP TABLE IF EXISTS User")
    cursor.execute("""
    CREATE TABLE User (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(8) NOT NULL,
        token VARCHAR(128) DEFAULT NULL,
        mailAddress VARCHAR(64) NOT NULL,
        name VARCHAR(64) DEFAULT NULL,
        status VARCHAR(16) DEFAULT 'user'
    )
    """)

    # 删除Booking表（如果存在），然后创建Booking表
    cursor.execute("DROP TABLE IF EXISTS Booking")
    cursor.execute(""" 
    CREATE TABLE Booking (
        id INT NOT NULL,
        date DATE NOT NULL,
        block INT NOT NULL,
        status BOOL NOT NULL,
        bookBy VARCHAR(8) DEFAULT NULL,
        UNIQUE (id, date, block)  -- 设置 (id, date, block) 组合为唯一
    )
    """)

    print("数据库和表已成功创建。")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("用户名或密码错误。")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("数据库不存在。")
    else:
        print(err)
finally:
    cursor.close()
    cnx.close()
