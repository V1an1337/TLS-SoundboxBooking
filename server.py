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


def getUsernameFromToken(token: str):
    # 验证token并获取用户名
    db = connection_pool.get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM User WHERE token = %s", (token,))
    user = cursor.fetchone()

    if user is None:
        return 0, "", None, None

    username = user[0]
    return 1, username, db, cursor


@app.route('/getSoundboxState', methods=['GET'])
def getSoundboxState():
    token = request.cookies.get('token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    getUsernameState, username, db, cursor = getUsernameFromToken(token)
    if getUsernameState == 0:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    try:
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
        cursor.close()
        db.close()


@app.route('/book', methods=['POST'])
def book():
    token = request.cookies.get('token')
    if not token:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    getUsernameState, username, db, cursor = getUsernameFromToken(token)
    if getUsernameState == 0:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    try:

        logging.info(f"/book {username} accessed the route.")

        # 获取Query参数并验证
        booking_id = request.args.get('id')
        booking_date = request.args.get('date')
        block = request.args.get('block')

        if not (booking_id and booking_date and block):
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)
        if not (booking_id.isdigit() and block.isdigit() and is_valid_date(booking_date)):
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)

        cursor.execute("SELECT * FROM Booking WHERE id = %s AND date = %s AND block = %s",
                       (booking_id, booking_date, block))
        booking = cursor.fetchone()

        if not booking:
            return make_response(jsonify({"error": "soundbox not found"}), 404)

        booking_status = booking[3]  # 假设 status 在 Booking 表中的位置为 3

        if booking_status:  # 已被预定
            logging.info(f"/book Attempt to book by {username} failed: Already booked.")
            return make_response(jsonify({"error": "Already booked"}), 400)

        # 更新 status 和 bookBy
        cursor.execute("UPDATE Booking SET bookBy = %s, status = true WHERE id = %s AND date = %s AND block = %s",
                       (username, booking_id, booking_date, block))
        db.commit()

        logging.info(f"/book Booking {booking_id} at block {block} in {booking_date} successful by {username}.")
        return jsonify({"status": True}), 200

    except Exception as e:
        logging.error(f"/book An error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
