import mysql.connector
import hashlib
from mysql.connector import errorcode

config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
    'database': 'SoundboxBooking',
}


def insert_user(username, password, mailAddress, token=None):
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        insert_query = "INSERT INTO User (username, password, mailAddress, token) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, hashed_password, mailAddress, token))
        cnx.commit()
        print("用户数据插入成功。")
    except mysql.connector.Error as err:
        print(f"插入用户时出错: {err}")
    finally:
        cursor.close()
        cnx.close()


def insert_booking(id, date, block, status, bookBy):

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        insert_query = "INSERT INTO Booking (id, date, block, status, bookBy) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (id, date, block, status, bookBy))
        cnx.commit()
        print("预约数据插入成功。")
    except mysql.connector.Error as err:
        print(f"插入预约时出错: {err}")
    finally:
        cursor.close()
        cnx.close()


# 示例数据插入
insert_user('user1234', 'password123', 'example@example.com', token="V1an1337")
insert_booking(1, '2024-09-24', 3, True, '20271064')
