import datetime
from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from datetime import timedelta
app = Flask(__name__)
DB_NAME = 'mylife.db'

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

@app.route('/worklife', methods=['GET'])
def get_worklife():
    comment = request.args.get("type")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM worklife WHERE sessionType=?", (comment,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)
@app.route('/todayf', methods=['GET'])
def get_todayf():
   # 连接数据库
    conn = sqlite3.connect('mylife.db')
    cursor = conn.cursor()

    # 获取当天数据
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = current_date + ' 00:00:00'
    end_date = current_date + ' 23:59:59'
    query = "SELECT * FROM worklife WHERE datetime >= ? AND datetime <= ? ORDER BY datetime"
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()

    conn.close()
    return jsonify(rows)
@app.route('/today', methods=['GET'])
def get_today():
    # 连接到SQLite数据库
    conn = sqlite3.connect('mylife.db')
    cursor = conn.cursor()

    # 获取当天日期
    today = datetime.datetime.now().date()
    # print(today)
    # 初始化各个任务在每个小时的累计sessionTime
    hourly_task_time = {task: [0] * 1 for task in set([row[4] for row in cursor.execute("SELECT * FROM worklife")])}
    print(hourly_task_time)
    # 查询当天每小时各任务的sessionTime
    start_time = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)  # 创建ISO格式的起始时间
    end_time = start_time + timedelta(hours=23)
    print(start_time, end_time)
        # 查询当天每小时各任务的sessionTime
    cursor.execute("SELECT sessionType, sessionTime FROM worklife WHERE datetime >= ? AND datetime < ?", (start_time, end_time))
    result = cursor.fetchall()
    print(result)
    # 处理查询结果
    for task, session_time in result:
            hourly_task_time[task][0] += session_time

    # 将每个任务在每个小时的累计sessionTime转换为字典形式
    hourly_task_time_dict = {task: hourly_task_time[task] for task in hourly_task_time}

    # 打印每个任务在每个小时的累计sessionTime
    for task, task_time_list in hourly_task_time_dict.items():
        print(f"任务 {task} 在每个小时的累计sessionTime为：{task_time_list}")

    # 关闭数据库连接
    # print(task_time_list)
    conn.close()
    return jsonify(hourly_task_time_dict)
@app.route('/max', methods=['GET'])
#查询worklife表中sessionTime的最大值
def get_max():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(sessionTime) FROM worklife" )
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)
# from datetime import datetime, timedelta
import datetime

@app.route('/month', methods=['GET'])
#查询worklife表中sessionTime的最大值
def get_month():
    conn = create_connection()
    cursor = conn.cursor()

    # 获取当月的起始日期和结束日期
    today = datetime.datetime.now()
    start_date = today.replace(day=1).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today.replace(day=1, month=today.month+1)

    # 查询当月的数据
    query = f"SELECT datetime, sessionType, sessionTime FROM worklife WHERE datetime >= '{start_date.isoformat()}' AND datetime < '{end_date.isoformat()}'"
    cursor.execute(query)
    rows = cursor.fetchall()

    # 计算每天各类 sessionType 的 sessionTime 总和
    data = {}
    for row in rows:
        date_str, session_type, session_time = row
        date = date_str.split('T')[0]
        # date = date.date()
        if date not in data:
            data[date] = {}
        if session_type not in data[date]:
            data[date][session_type] = 0
        data[date][session_type] += session_time

    # 按照指定格式返回 pieSeries
    pieSeries = []
    for date, sessions in data.items():
        pieSeries.append({
            'type': 'pie',
            'id': f'pie-{date}',
            'center': date,
            'radius': 60,
            'coordinateSystem': 'calendar',
            'label': {
                'formatter': '{c}',
                'position': 'inside',
                'fontsize':20
            },
            'data': [
                {'name': '工作', 'value': sessions.get('工作', 0)},
                {'name': '学习', 'value': sessions.get('学习', 0)},
                {'name': '吃饭', 'value': sessions.get('吃饭', 0)},
                {'name': '娱乐', 'value': sessions.get('娱乐', 0)},
                {'name': '睡觉', 'value': sessions.get('睡觉', 0)}
            ]
        })

    # 关闭数据库连接
    conn.close()
    return jsonify(pieSeries)
@app.route('/worklife', methods=['POST'])
def add_worklife():
    data = request.get_json()
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO worklife (datetime, sessionTime, sessionTask, sessionType) VALUES (?, ?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3], data['sessionTime'], data['sessionTask'], data['sessionType']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Record added successfully"})

@app.route('/worklife/<int:worklife_id>', methods=['PUT'])
def update_worklife(worklife_id):
    data = request.get_json()
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE worklife SET datetime=?, sessionTime=?, sessionTask=? WHERE id=?", (data['datetime'], data['sessionTime'], data['sessionTask'], worklife_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Record updated successfully"})

@app.route('/worklife/<int:worklife_id>', methods=['DELETE'])
def delete_worklife(worklife_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM worklife WHERE id=?", (worklife_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Record deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
