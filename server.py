import logging
from flask import Flask, request, jsonify, make_response
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import re

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename="server.log")

app = Flask(__name__)

# 数据库连接池配置
config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
    'database': 'SoundboxBooking',
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **config)


def is_valid_date(date_str):
    """ 验证日期格式 YYYY-MM-DD """
    return bool(re.match(r"^\d{4}\d{2}\d{2}$", date_str))


@app.route('/getSoundboxState', methods=['GET'])
def get_soundbox_state():
    token = request.cookies.get('token')
    db = None
    cursor = None

    try:
        # 验证token并获取用户名
        db = connection_pool.get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM User WHERE token = %s", (token,))
        user = cursor.fetchone()

        if user is None:
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        username = user[0]
        logging.info(f"/getSoundboxState {username} accessed the route.")

        # 获取Query参数并验证
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        if (start_date and not is_valid_date(start_date)) or (end_date and not is_valid_date(end_date)):
            return make_response(jsonify({"error": "Invalid date format"}), 400)

        if start_date and end_date:
            cursor.execute(
                "SELECT id, DATE_FORMAT(date, '%Y%m%d'), block, status FROM Booking WHERE date BETWEEN %s AND %s",
                (start_date, end_date))
        else:
            today = datetime.now().date()
            cursor.execute("SELECT id, DATE_FORMAT(date, '%Y%m%d'), block, status FROM Booking WHERE date = %s",
                           (today,))

        results = cursor.fetchall()
        formatted_results = [(id, str(date), block, status) for (id, date, block, status) in results]

        # 记录返回结果
        logging.info(f"/getSoundboxState Retrieved results from user {username}: {formatted_results}")
        return jsonify(formatted_results)

    except Exception as e:
        logging.error(f"/getSoundboxState An error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


if __name__ == '__main__':
    app.run(debug=True)
