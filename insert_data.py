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

    # 插入未来工作日（周一到周五）数据
    def insert_weekday_data(self):
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as cursor:
                error_count = 0
                for i in range(7):
                    date = datetime.now().date() + timedelta(days=i)
                    if date.weekday() < 5:  # 只插入周一到周五的数据
                        for id in range(1, 61):
                            for block in range(1, 11):
                                insert_sql = """
                                            INSERT INTO Booking (id, date, block, status, bookBy) 
                                            VALUES (%s, %s, %s, %s, %s)
                                            """
                                values = (id, date, block, False, None)
                                try:
                                    cursor.execute(insert_sql, values)
                                except mysql.connector.IntegrityError:
                                    error_count += 1
                logging.info(f"error_count = {error_count}")

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

    def job(self):
        s = time.time()
        logging.info("自动插入/清理启动！")
        self.insert_weekday_data()
        self.delete_past_week_weekday_data()
        logging.info(f"执行完毕，耗时：{time.time() - s}")

    def init(self):
        self.job()

    # 启动自动任务：每周天凌晨执行
    def start(self):
        # 每周天（周日）凌晨 00:00 执行任务
        schedule.every().sunday.at("00:00").do(self.job)
        logging.info("定时任务已经在运行")

        # 创建一个独立的线程来运行调度器，确保非阻塞
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        # 使用后台线程执行调度器
        threading.Thread(target=run_scheduler, daemon=True).start()