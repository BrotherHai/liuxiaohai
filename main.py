import botpy
from botpy import logging, BotAPI

from botpy.ext.command_util import Commands
from botpy.message import Message
from botpy.ext.cog_yaml import read
import sqlite3
import random
from datetime import datetime

_log = logging.get_logger()


@Commands("签到")
async def sign(api: BotAPI, message: Message, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    user_id = message.author.id
    # 连接到SQLite数据库
    conn = sqlite3.connect('./data/score.db')
    cursor = conn.cursor()

    # 获取当前日期
    today = datetime.now().date()

    # 查询用户表获取用户信息
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        # 查询用户的签到记录
        cursor.execute("SELECT * FROM sign_ins WHERE user_id=? AND date=?", (user_id, today))
        sign_in_record = cursor.fetchone()

        if sign_in_record:
            print("今天已经签到过了！")
            cursor.close()
            conn.close()
            await message.reply(content=f"今天已经签到过了！")

        else:
            # 随机生成积分
            points = random.randint(1, 10)
            print
            # 更新用户表中的积分
            new_points = user[2] + points
            cursor.execute("UPDATE users SET points=? WHERE id=?", (new_points, user_id))

            # 插入签到记录
            cursor.execute("INSERT INTO sign_ins (user_id, date, points) VALUES (?, ?, ?)", (user_id, today, points))
            conn.commit()

            print(f"签到成功！获得{points}积分，当前总积分为{new_points}")
            # 关闭数据库连接
            cursor.close()
            conn.close()
            await message.reply(content=f"签到成功！获得{points}积分，当前总积分为{new_points}")
    else:
        print("用户不存在！")


@Commands("商城")
async def shop(api: BotAPI, message: Message, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    user_id = message.author.id
    # 连接到SQLite数据库
    conn = sqlite3.connect('./data/score.db')
    cursor = conn.cursor()
    # 查询所有商品信息
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    contents = ''
    contents += "商品信息：\n"
    for product in products:
        contents += "名称：{}\n价格：{}\n描述：{}\n库存：{}\n**********\n".format(product[1], product[2], product[4],
                                                                              product[5])
    contents += "回复 ‘/兑换+物品名称’进行兑换"
    await message.reply(content=contents)

    # 关闭数据库连接
    cursor.close()
    conn.close()


@Commands("我的物品")
async def my_bags(api: BotAPI, message: Message, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    user_id = message.author.id
    # 连接到SQLite数据库
    conn = sqlite3.connect('./data/score.db')
    cursor = conn.cursor()
    try:

        cursor.execute("SELECT * FROM warehouse WHERE user_id = ?", (user_id,))
        purchase = cursor.fetchall()

        if purchase:
            contents = ''
            contents += message.author.username+"的物品信息：\n"
            for product in purchase:
                contents += "名称：{}\n库存：{}\n**********\n".format(product[2], product[3])
            contents += "回复 ‘/使用+物品名称’进行使用"
            await message.reply(content=contents)
        else:
            await message.reply(content='你还没有物品！')

    except Exception as e:
        await message.reply(content="查询失败")
        print("查询失败:", str(e))

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()


@Commands("兑换")
async def buy(api: BotAPI, message: Message, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    user_id = message.author.id
    # 连接到SQLite数据库
    conn = sqlite3.connect('./data/score.db')
    cursor = conn.cursor()
    product_name = message.content.split(' ')[-1]
    print(product_name)
    try:
        # 查询用户是否存在
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            await message.reply(content="用户不存在")
            return
        # 查询商品是否存在
        cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
        product = cursor.fetchone()
        if not product:
            await message.reply(content="物品不存在")
            return

        # 检查商品库存
        if product[5] == 0:
            await message.reply(content="商品库存不足")
            return

            # 查询用户是否已购买过该商品
        cursor.execute("SELECT * FROM warehouse WHERE user_id = ? AND product_id = ?", (user_id, product[0]))
        purchase = cursor.fetchone()

        if purchase:
            # 更新购买记录
            new_quantity = purchase[3] + 1
            cursor.execute("UPDATE warehouse SET quantity = ? WHERE id = ?", (new_quantity, purchase[0]))
        else:
            # 插入购买记录到warehouse表
            quantity = 1  # 购买数量，这里假设为1
            cursor.execute("INSERT INTO warehouse (user_id, product_id, quantity) VALUES (?, ?, ?)",
                           (user_id, product_name, quantity))

        # 更新用户积分
        new_points = user[2] - product[2]
        cursor.execute("UPDATE users SET points = ? WHERE id = ?", (new_points, user_id))

        # 更新商品库存
        new_stock = product[5] - 1
        cursor.execute("UPDATE products SET quantity = ? WHERE name = ?", (new_stock, product_name))

        conn.commit()
        await message.reply(content="兑换成功")
        print("兑换成功")

    except Exception as e:
        await message.reply(content="兑换失败")
        print("兑换失败:", str(e))

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()
@Commands("使用")
async def use(api: BotAPI, message: Message, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    user_id = message.author.id
    # 连接到SQLite数据库
    conn = sqlite3.connect('./data/score.db')
    cursor = conn.cursor()
    product_name = message.content.split(' ')[-1]
    print(product_name)
    try:
        # 查询用户是否存在
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            await message.reply(content="用户不存在")
            return
        # 查询商品是否存在
        cursor.execute("SELECT * FROM warehouse WHERE product_id = ? and user_id = ?", (product_name,user_id))
        purchase = cursor.fetchone()
        if not purchase:
            await message.reply(content="物品不存在")
            return

        # 检查商品库存
        if purchase[3] == 0:
            await message.reply(content="商品库存不足")
            return

        if purchase:
            # 更新购买记录
            new_quantity = purchase[3] - 1
            cursor.execute("UPDATE warehouse SET quantity = ? WHERE id = ?", (new_quantity, purchase[0]))


        conn.commit()
        await message.reply(content="使用成功")
        print("使用成功")

    except Exception as e:
        await message.reply(content="使用失败")
        print("使用失败:", str(e))

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

class MyClient(botpy.Client):
    async def on_at_message_create(self, message: Message):
        handlers = [
            sign,
            shop,
            buy,
            my_bags,
            use
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return


intents = botpy.Intents(public_guild_messages=True)
client = MyClient(intents=intents)
client.run(appid='102004094', token='PEnXUOglUA8EAn6dpIWAMRw7vGEu9LfX')
