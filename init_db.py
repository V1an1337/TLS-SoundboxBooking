import mysql.connector
from mysql.connector import errorcode
import hashlib

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

    # 创建User表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(8) NOT NULL,
        password VARCHAR(32) NOT NULL,
        mailAddress VARCHAR(255) NOT NULL,
        token VARCHAR(256) DEFAULT NULL
    )
    """)

    # 创建Booking表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Booking (
        id INT NOT NULL,
        date DATE NOT NULL,
        block INT CHECK (block BETWEEN 1 AND 10),
        status BOOL NOT NULL,
        bookBy VARCHAR(8) DEFAULT NULL
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
