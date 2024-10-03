import mysql.connector
from datetime import datetime, timedelta
import threading
import schedule
import time
import logging

# MySQL连接配置
config = {
    'user': 'soundbox',
    'password': 'V1an1337',
    'host': '127.0.0.1',
    'database': 'SoundboxBooking',
}

class InsertData:
    def __init__(self):
        pass

    # 插入未来两周工作日（周一到周五）数据
    def insert_weekday_data(self):
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as cursor:
                for i in range(14):
                    date = datetime.now().date() + timedelta(days=i)
                    if date.weekday() < 5:  # 只插入周一到周五的数据
                        for id in range(1, 61):
                            for block in range(1, 11):
                                # 先检查是否已经存在该数据
                                check_sql = """
                                           SELECT COUNT(*) FROM Booking 
                                           WHERE id = %s AND date = %s AND block = %s
                                           """
                                cursor.execute(check_sql, (id, date, block))
                                (count,) = cursor.fetchone()
                                # 如果不存在该记录，才插入数据
                                if count == 0:
                                    insert_sql = """
                                               INSERT INTO Booking (id, date, block, status, bookBy) 
                                               VALUES (%s, %s, %s, %s, %s)
                                               """
                                    values = (id, date, block, False, None)
                                    cursor.execute(insert_sql, values)

                conn.commit()
        logging.info("工作日数据插入完成！")

    # 清理两周前数据
    def delete_past_week_weekday_data(self):
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as cursor:
                one_week_ago = datetime.now().date() - timedelta(days=14)
                sql = """
                DELETE FROM Booking WHERE date < %s
                """
                cursor.execute(sql, (one_week_ago,))
                conn.commit()
        logging.info("过去一周的工作日数据已删除！")

    # 启动自动任务：每周天凌晨执行
    def start(self):
        def job():
            logging.info("自动插入/清理启动！")
            self.insert_weekday_data()
            self.delete_past_week_weekday_data()

        # 每周天（周日）凌晨 00:00 执行任务
        schedule.every().sunday.at("00:00").do(job)
        logging.info("定时任务已经在运行，无需重复启动。")

        # 创建一个独立的线程来运行调度器，确保非阻塞
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        # 使用后台线程执行调度器
        threading.Thread(target=run_scheduler, daemon=True).start()