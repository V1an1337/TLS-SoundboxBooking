import logging
import identity
import identity.web
from flask import Flask, redirect, render_template, request, session, url_for, jsonify, make_response
import requests
from mysql.connector import pooling
from datetime import datetime
import re
from flask_session import Session
import app_config
from insert_data import InsertData

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename="server.log")

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

from werkzeug.middleware.proxy_fix import ProxyFix  # Microsoft登录示例里的依赖

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config.get("AUTHORITY"),
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

# 数据库连接池配置
config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
    'database': 'SoundboxBooking',
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **config)

insert_data = InsertData()  # 启动自动插入/删除程序
insert_data.start()


def is_valid_date(date_str):
    """ 验证日期格式 YYYY-MM-DD """
    return bool(re.match(r"^\d{4}\d{2}\d{2}$", date_str))


def getUsernameFromToken(token: str, autoClose=False):
    # 验证token并获取用户名
    db = connection_pool.get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM User WHERE token = %s", (token,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        db.close()
        return 0, "", None, None

    username = user[0]
    if autoClose:
        cursor.close()
        db.close()

    return 1, username, db, cursor


@app.route("/login")
def login():
    token = request.cookies.get('token')
    if not token:  # token为空
        return render_template("login.html", version=identity.__version__, **auth.log_in(
            scopes=app_config.SCOPE,  # Have user consent to scopes during log-in
            redirect_uri=url_for("auth_response", _external=True),
        ))

    getUsernameState, username, db, cursor = getUsernameFromToken(token, autoClose=True)  # 不需要手动cursor.close,db.close
    if getUsernameState == 0:  # token不匹配
        return render_template("login.html", version=identity.__version__, **auth.log_in(
            scopes=app_config.SCOPE,  # Have user consent to scopes during log-in
            redirect_uri=url_for("auth_response", _external=True),
        ))

    return jsonify({"status": True}), 200  # token匹配


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)

    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))

    try:
        # 获取个人信息
        logging.info(f"{app_config.REDIRECT_PATH} getting information...")
        api_result = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={'Authorization': 'Bearer ' + token['access_token']},
            timeout=30,
        ).json()

        mailAddress = api_result['mail']
        validMail = str(mailAddress).split("@")
        if not (len(validMail) == 2 and validMail[1].lower() == "tsinglan.org"):  # valid mailAddress
            return jsonify({"error": "Unauthorized"}), 401

        username = str(api_result['jobTitle'])[1:]  # T20271064把T去掉
        new_token = token["access_token"][:128]

        logging.info(f"/getAToken-getAPI user {username} accessed with mail {validMail}")

    except Exception as e:
        logging.error(f"/getAToken-getAPI An error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

    db = connection_pool.get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT username FROM User WHERE mailAddress = %s", (mailAddress,))
        user = cursor.fetchone()

        if user is None:  # 新用户注册
            logging.info(f"/getAToken-UpdateUser/Token user {username} with main {mailAddress} registered!")
            insert_query = "INSERT INTO User (username, mailAddress, token) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, mailAddress, new_token))
        else:  # 更新token
            logging.info(f"/getAToken-UpdateUser/Token user {username} renewed token!")
            cursor.execute("UPDATE User SET token = %s WHERE mailAddress = %s",
                           (new_token, mailAddress))

        db.commit()
        return jsonify({"status": True, "token": new_token}), 200
    except Exception as e:
        logging.error(f"/getAToken-UpdateUser/Token An error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)
    finally:
        cursor.close()
        db.close()


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=identity.__version__)


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
            logging.info(f"/getSoundboxState Invalid date format from user {username}")
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


@app.route('/getSoundboxBookBy', methods=['GET'])
def getSoundboxBookBy():
    token = request.cookies.get('token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    getUsernameState, username, db, cursor = getUsernameFromToken(token)
    if getUsernameState == 0:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    try:
        logging.info(f"/getSoundboxBookBy {username} accessed the route.")

        booking_id = request.args.get('id')
        booking_date = request.args.get('date')
        block = request.args.get('block')

        if not (booking_id and booking_date and block):
            logging.info(
                f"/getSoundboxBookBy Attempt to getSoundbox by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)
        if not (booking_id.isdigit() and block.isdigit() and is_valid_date(booking_date)):
            logging.info(
                f"/getSoundboxBookBy Attempt to getSoundbox by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)

        cursor.execute("SELECT * FROM Booking WHERE id = %s AND date = %s AND block = %s",
                       (booking_id, booking_date, block))
        booking = cursor.fetchone()

        if not booking:
            logging.info(f"/getSoundboxBookBy Attempt to getSoundbox by {username} failed: Soundbox not found.")
            return make_response(jsonify({"error": "Soundbox not found"}), 404)

        booking_status, booking_by = booking[3], booking[4]  # 假设 status 在 Booking 表中的位置为 3
        formatted_results = [booking_status, booking_by]

        # 记录返回结果
        logging.info(f"/getSoundboxBookBy Retrieved results from user {username}: {formatted_results}")
        return jsonify(formatted_results)

    except Exception as e:
        logging.error(f"/getSoundboxBookBy An error occurred: {e}")
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
            logging.info(f"/book Attempt to book by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)
        if not (booking_id.isdigit() and block.isdigit() and is_valid_date(booking_date)):
            logging.info(f"/book Attempt to book by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)

        cursor.execute("SELECT * FROM Booking WHERE id = %s AND date = %s AND block = %s",
                       (booking_id, booking_date, block))
        booking = cursor.fetchone()

        if not booking:
            logging.info(f"/book Attempt to book by {username} failed: Soundbox not found.")
            return make_response(jsonify({"error": "Soundbox not found"}), 404)

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


@app.route('/unbook', methods=['POST'])
def unbook():
    token = request.cookies.get('token')
    if not token:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    getUsernameState, username, db, cursor = getUsernameFromToken(token)
    if getUsernameState == 0:
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    try:

        logging.info(f"/unbook {username} accessed the route.")

        # 获取Query参数并验证
        booking_id = request.args.get('id')
        booking_date = request.args.get('date')
        block = request.args.get('block')

        if not (booking_id and booking_date and block):
            logging.info(f"/book Attempt to book by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)
        if not (booking_id.isdigit() and block.isdigit() and is_valid_date(booking_date)):
            logging.info(f"/book Attempt to book by {username} failed: Missing or wrong id/date/block.")
            return make_response(jsonify({"error": "Missing or wrong id/date/block"}), 400)

        cursor.execute("SELECT * FROM Booking WHERE id = %s AND date = %s AND block = %s",
                       (booking_id, booking_date, block))
        booking = cursor.fetchone()

        if not booking:
            logging.info(f"/book Attempt to book by {username} failed: Soundbox not found.")
            return make_response(jsonify({"error": "Soundbox not found"}), 404)

        booking_status, booking_by = booking[3], booking[4]  # 假设 status 在 Booking 表中的位置为 3

        if not (booking_status and booking_by == username):  # 不是被当前用户预定
            logging.info(f"/unbook Attempt to unbook by {username} failed: Not booked or booked by the current user.")
            return make_response(jsonify({"error": "Not booked or booked by the current user"}), 400)

        # 更新 status 和 bookBy
        cursor.execute("UPDATE Booking SET bookBy = %s, status = false WHERE id = %s AND date = %s AND block = %s",
                       (None, booking_id, booking_date, block))
        db.commit()

        logging.info(f"/unbook Unbooking {booking_id} at block {block} in {booking_date} successful by {username}.")
        return jsonify({"status": True}), 200

    except Exception as e:
        logging.error(f"/book An error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    app.run()
