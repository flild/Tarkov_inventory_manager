import logging
import sqlite3
import os
import re
from aiogram import Bot, Dispatcher, executor, types
from config import bot_token
# Configure logging
logging.basicConfig(level=logging.INFO)


# Initialize bot and dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
db_path = 'inventory_bd.db'


def bd_insert(msg_text):
    if os.path.exists(db_path):
        inv_bd_conn = sqlite3.connect(db_path)
        inv_bd_cursor = inv_bd_conn.cursor()
        match = re.match(r'(\D*)(\d*)',msg_text)
        name = match[1].replace(' ','')
        if match[2] != '':
            count = int(match[2])
        else:
            count = 1
        inv_bd_cursor.execute("SELECT * FROM inventory WHERE item_name = ?",(name,))
        item = inv_bd_cursor.fetchone()
        if item == None:
            inv_bd_cursor.execute("INSERT INTO inventory (item_name, count , target) VALUES ( ?, ?, ?);",
                                  (name, count, 0))
            inv_bd_conn.commit()
            inv_bd_cursor.execute("SELECT * FROM inventory WHERE item_name = ?",(name,))
            item = inv_bd_cursor.fetchone()
        else:
            inv_bd_cursor.execute("UPDATE inventory SET count = ? WHERE  item_name = ?", (item[2] + count, item[1],))
            inv_bd_conn.commit()
        inv_bd_conn.close()
        return item
    else:
        inv_bd_conn = sqlite3.connect(db_path)
        inv_bd_cursor = inv_bd_conn.cursor()
        inv_bd_cursor.execute("""CREATE TABLE IF NOT EXISTS inventory(
           item_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           item_name TEXT,
           count INT,
           target INT);
        """)
        inv_bd_conn.commit()
        inv_bd_conn.close()
        bd_insert(msg_text)


@dp.message_handler(commands=['start', 'help'])
async def start_massge(message: types.Message):
    await message.answer("Привет \n Я помогу следить за твоим инвентарём")

@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_item(message: types.Message):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM inventory where item_id = ?',(int(message.text[4:]),))
    conn.commit()
    conn.close()
    await message.answer('удалено')

@dp.message_handler(lambda message: message.text.startswith('/inv'))
async def show_inventory(message:types.Message):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    msg = ''
    cur.execute('SELECT * FROM inventory')
    for row in cur.fetchall():
        msg+= f'{row[0]} {row[1]} {row[2]}/{row[3]}\n'
    conn.commit()
    conn.close()
    await message.answer(msg)
@dp.message_handler()
async def echo(message: types.Message):
    item = bd_insert(message.text.lower())
    await message.answer(f'Записал\n'
                         f'id {item[0]}\n'
                         f'{item[1]} {item[2]}/{item[3]}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
