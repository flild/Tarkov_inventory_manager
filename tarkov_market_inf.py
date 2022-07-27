
from keyboard import add_hotkey, wait

import requests
import json
from selenium import webdriver

import tkinter as tk
from overlay import Window

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import telebot
from config_file.config import bot_token, my_tlg_id
from image_prepare import pic, do_scrnshot_and_convert

bot = telebot.TeleBot(bot_token, parse_mode=None)

# Ошибки
# 1 не распозналось
# 2 ошибка парсинга
# 3 слишком частые запросы


def ocr_space_file(filename, overlay=False, api_key='helloworld', language='rus'):
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()


def parser_tarkov_market(recognize_result):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(executable_path=r'C:\\Files\\geckodriver.exe', options=options,  log_path='./Logs/geckodriver.log')
    driver.get("https://tarkov-market.com/ru/")
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div[2]/div[1]/input").send_keys(
            recognize_result)
        time.sleep(1)
        res = driver.find_element(By.XPATH,
                                  "/html/body/div[1]/div/div/div/div[2]/div[2]/div[5]/div[2]/div[4]/div/span").text
        mes = res + ' ' + recognize_result
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption=mes)

    except Exception as e:
        print('хуита', e)
        mes = recognize_result + ' не найден'
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption=mes)
    finally:
        driver.close()


def wait_words(lang):
    print(lang)
    do_scrnshot_and_convert()
    answer = ocr_space_file('src/result.png', language=lang)
    if answer == 'You may only perform this action upto maximum 10 number of times within 600 seconds':
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №3. Ты слишком быстрый')
        return
    try:
        json_data = json.loads(answer)
        sec_json_data = json_data.get('ParsedResults')[0]
        recognize_result = sec_json_data['ParsedText']
    except AttributeError:
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №1. Не распозналось')
        return
    print(recognize_result)
    if recognize_result == '':
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №2. пусто')
        return
    parser_tarkov_market(recognize_result)


if __name__ == '__main__':
    def main():

        add_hotkey("num 7", lambda: wait_words("rus"))
        add_hotkey("num 9", lambda: wait_words("eng"))
        while True:
            wait('esc')
    main()
