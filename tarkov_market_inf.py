import keyboard
import pyautogui
from PIL import ImageGrab
import numpy as np
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import telebot
from config import bot_token, my_tlg_id

bot = telebot.TeleBot(bot_token, parse_mode=None)
pic = 'MySnapshot.png'
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


while True:
    keyboard.wait("num 7")
    x, y = pyautogui.position()
    w = x + 35
    h = y + 35
    x = x - 35
    y = y - 35
    snapshot = ImageGrab.grab(bbox=(x, y, w, h))
    save_path = "MySnapshot.png"
    snapshot.save(save_path)
    answer = ocr_space_file(pic)
    if answer == 'You may only perform this action upto maximum 10 number of times within 600 seconds':
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №3. Ты слишком быстрый')
        continue
    try:
        json_data = json.loads(answer)
        sec_json_data = json_data.get('ParsedResults')[0]
        recognize_result = sec_json_data['ParsedText']
    except AttributeError:
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №1. Не распозналось')
        continue
    print(recognize_result)
    if recognize_result == '':
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption='Ошибка №2. пусто')
        continue
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(executable_path=r'C:\\Files\\geckodriver.exe', options=options)
    driver.get("https://tarkov-market.com/ru/")
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div[2]/div[1]/input").send_keys(
            recognize_result)
        time.sleep(1)
        res = driver.find_element(By.XPATH,
                                  "/html/body/div[1]/div/div/div/div[2]/div[2]/div[5]/div[2]/div[4]/div/span").text
        mes = res + ' ' + recognize_result
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption=res)
    except Exception as e:
        print('хуита', e)
        res = recognize_result + ' не найден'
        bot.send_photo(chat_id=my_tlg_id, photo=open(pic, 'rb'), caption=res)
    finally:
        driver.close()
# res['ParsedResults']['ParsedText']
