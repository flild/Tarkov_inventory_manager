import logging
import sqlite3
import os
import re
import keyboard
import threading
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ShippingOption, ShippingQuery, LabeledPrice
from config import bot_token, sberbank_payment
import asyncio

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
        match = re.match(r'(\D*)(\d*)', msg_text)
        name = match[1].replace(' ', '')
        if match[2] != '':
            count = int(match[2])
        else:
            count = 1
        inv_bd_cursor.execute("SELECT * FROM inventory WHERE item_name = ?", (name,))
        item = inv_bd_cursor.fetchone()
        if item == None:
            inv_bd_cursor.execute("INSERT INTO inventory (item_name, count , target) VALUES ( ?, ?, ?);",
                                  (name, count, 0))
            inv_bd_conn.commit()
            inv_bd_cursor.execute("SELECT * FROM inventory WHERE item_name = ?", (name,))
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
async def start_massge(message: Message):
    await message.answer("Привет \n Я помогу следить за твоим инвентарём")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_item(message: Message):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM inventory where item_id = ?', (int(message.text[4:]),))
    conn.commit()
    conn.close()
    await message.answer('удалено')


@dp.message_handler(lambda message: message.text.startswith('/inv'))
async def show_inventory(message: Message):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    msg = ''
    cur.execute('SELECT * FROM inventory')
    for row in cur.fetchall():
        msg += f'{row[0]} {row[1]} {row[2]}/{row[3]}\n'
    conn.commit()
    conn.close()
    await message.answer(msg)


# ________________________________________________________________________________________________________________________
prices = [LabeledPrice(label='Подписка на 30 дней', amount=10000)]

shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add(LabeledPrice('Pickup', 300))]


@dp.message_handler(lambda message: message.text.startswith('/buy'))
async def command_pay(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title='Купить подписку',
        description=' Want to visit your great-great-great-grandparents? Make a fortune at the races? Shake hands with Hammurabi and take a stroll in the Hanging Gardens? Order our Working Time Machine today!',
        payload='some_invoice',
        provider_token=sberbank_payment,
        currency='RUB',
        prices=prices,
        photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        start_parameter='time-machine-example')


@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query):
    print(shipping_query)
    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                                    error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                      " try to pay again in a few minutes, we need a small rest.")


@dp.message_handler(content_types=['successful_payment'])
async def got_payment(message):
    await bot.send_message(message.chat.id,
                           'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                           'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                               message.successful_payment.total_amount / 100, message.successful_payment.currency),
                           parse_mode='Markdown')


# ____________________________________________________________________________________________________________________________
@dp.message_handler()
async def echo(message: Message):
    if message.text[0] == '/':
        await message.answer(f'Ничего не понял')
        return
    item = bd_insert(message.text.lower())
    await message.answer(f'Записал\n'
                         f'id {item[0]}\n'
                         f'{item[1]} {item[2]}/{item[3]}')




if __name__ == '__main__':
    from payment_handler import dp
    executor.start_polling(dp, skip_updates=True)



