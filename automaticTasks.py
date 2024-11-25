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
        self.init()

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


class BlockManager:
    def __init__(self):
        # Block 开始时间
        self.timePeriod = ["8:00", "8:40", "9:20", "10:50", "11:40", "12:30", "14:05", "14:55", "15:40", "16:45",
                           "17:40"]  # 17:40 为B10结束时间，此时应重置为Block1，不然不能预定明天的静音仓
        # format timePeriod
        self.timePeriod = [datetime.strptime(time, '%H:%M').strftime('%H:%M') for time in self.timePeriod]

        # 检测现在的时间进行到哪个block
        self.updateBlock()

    def getCurrentBlock(self):
        current_time = datetime.now().strftime('%H:%M')
        for i, time in enumerate(self.timePeriod):
            if current_time < time:
                return i  # Return the block that has just passed or is currently in progress
        return len(self.timePeriod)  # Return the last block if current time is beyond all blocks

    def resetBlock(self):
        self.block = 1  # range: 1~10

    def updateBlock(self):
        self.block = self.getCurrentBlock()

        if self.block == 11:
            self.resetBlock()
        logging.info(f"Block 更新为 {self.block}")

    def start(self):
        for time in self.timePeriod:
            schedule.every().day.at(time).do(self.updateBlock)
        logging.info("UpdateBlock 定时任务已经在运行")
