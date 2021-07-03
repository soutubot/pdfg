# -*- codeing = utf-8 -*-
# @Time : 2021/6/4 18:35
# @Autor : Soutubot
# @File : pdfg-bot.py
# @Software : PyCharm
# 匯入相關套件
from PIL import Image
import re
import requests
import base64
import time
import datetime
from urllib import parse
from bs4 import BeautifulSoup
import telebot
import os
import urllib.parse
import imagehash
import random

session = requests.session()

#-----↓需要你修改的参数↓-----
bot_token = '123456:xxxxxx' #TG BOT API
bot = telebot.TeleBot(bot_token)
bot_nanme = "@pdfg_bot" #bot名称暂时没什么卵用
group_id = -123456 #群组白名单id
admin_id = 654321 #admin白名单id
Channel_url = 't.me/xxx/' #频道链接
dir_name = './download-telegram-channel-pictures/picture_storage_path/' #本地图库位置
#-----↑需要你修改的参数↑-----

#--------------------pdfg指令_开始--------------------
@bot.message_handler(commands=['pdfg'])

def send_pdfg(message):
    print(message)
    if message.chat.type == 'supergroup' and message.chat.id == group_id: #判断是否本群
        if_sousuo(message)
    elif message.chat.type == 'private' and message.chat.id == admin_id:  #判断是否admin
        if_sousuo(message)
    else:
        print('非群聊&非本群&非admin')

#判断消息是否为回复和图片
def if_sousuo(message):
    if message.reply_to_message is not None:  # 判断是否为回复
        if message.reply_to_message.content_type == 'photo':  # 判断回复内容是否为图片
            image_url = bot.get_file_url(message.reply_to_message.photo[-1].file_id)
            bot.reply_to(message.reply_to_message, text="正在搜索中，请等待30秒", parse_mode="MarkdownV2")
            sousuo(image_url, message.reply_to_message)
        elif message.reply_to_message.content_type == 'document': #判断文件内容是否为图片
            try:
                document_url = bot.get_file_url(message.reply_to_message.document.file_id)
                if '.jpeg' or '.jpg' or '.png' in document_url:
                    bot.reply_to(message.reply_to_message, text="正在搜索中，请等待30秒", parse_mode="MarkdownV2")
                    sousuo(document_url, message.reply_to_message)
            except:
                bot.reply_to(message.reply_to_message, text="请使用指令回复一张图片，暂不支持GIF和视频，图片文件大于20M也不行")
        else:
            bot.reply_to(message.reply_to_message, text="请使用指令回复一张图片，暂不支持GIF和视频")
    else:
        bot.reply_to(message, text="请使用指令回复一张图片，暂不支持GIF和视频")

#开始匹配
def sousuo(image_url, message):
    start = time.time()
    file_list = os.listdir(dir_name) #获取指定目录的文件列表
    phash_img = imagehash.phash(Image.open(requests.get(image_url, stream=True).raw)) #计算image_url的phash
    print(f'{image_url} - phash值 - {phash_img}')

    #计算所有本地库图片的phash，并与'phash_img'计算对比数值
    phashall_value = []
    for i in file_list :
        phash = imagehash.phash(Image.open(f'{dir_name}{i}')) #先计算所有本地库图片的phash
        value = (phash - phash_img) / len(phash.hash) ** 2 #再与'phash_img'计算对比数值
        phashall_value.append(f'{value}')
    end = time.time()
    print (f'计算耗时{end - start}秒')

    #判断是否有发过
    if float(min(phashall_value)) < 0.18 : #判断是否有低于0.18数值
        img_name_OK = file_list[phashall_value.index(min(phashall_value))] #返回最小值的对应图片名
        head, sep, tail = img_name_OK.partition('-')
        img_name_OK_ID = head.replace(".jpg","").replace(".png","")
        print(f'频道发过bot提醒您：频道发过！{Channel_url}{img_name_OK_ID}')
        bot.reply_to(message, text=f'频道发过bot提醒您：\n频道发过！ {Channel_url}{img_name_OK_ID}')
    else:
        img_name_OK = file_list[phashall_value.index(min(phashall_value))]
        head, sep, tail = img_name_OK.partition('-')
        img_name_OK_ID = head.replace(".jpg","").replace(".png","")
        print(f'未匹配到，最小值是{min(phashall_value)} | {Channel_url}{img_name_OK_ID}')
        bot.reply_to(message, text=f'未匹配到\n最小值是{min(phashall_value)} | {Channel_url}{img_name_OK_ID}')
#--------------------pdfg指令_结束--------------------

'''-----------------------------------------------------'''

#--------------------pdfgadd指令_开始--------------------
@bot.message_handler(commands=['pdfgadd'])
def send_pdfgadd(message):
    print(message)
    if message.chat.type == 'supergroup' and message.chat.id == group_id and message.from_user.id == admin_id: #判断是否本群且admin
        if_pdfgadd(message)
    elif message.from_user.username == 'GroupAnonymousBot':
        if_pdfgadd(message)
    elif message.chat.type == 'private' and message.chat.id == admin_id:  #判断是否admin
        if_pdfgadd(message)
    else:
        print('非群聊&非本群&非admin')

#判断消息是否为回复和图片
def if_pdfgadd(message):
    if message.reply_to_message is not None:  # 判断是否为回复
        if message.reply_to_message.content_type == 'photo':  # 判断回复内容是否为图片
            image_url = bot.get_file_url(message.reply_to_message.photo[-1].file_id)
            if_dl(image_url, message)
        elif message.reply_to_message.content_type == 'document': #判断文件内容是否为图片
            try:
                document_url = bot.get_file_url(message.reply_to_message.document.file_id)
                if '.jpeg' or '.jpg' or '.png' in document_url:
                    if_dl(document_url, message)
            except:
                bot.reply_to(message.reply_to_message, text="请使用指令回复一张图片，暂不支持GIF和视频，图片文件大于20M也不行")
        else:
            bot.reply_to(message.reply_to_message, text="请使用指令回复一张图片，暂不支持GIF和视频")
    else:
        bot.reply_to(message, text="请使用指令回复一张图片，暂不支持GIF和视频")

#判断格式是否正确
def if_dl(image_url, message):
    name_id = message.text.replace(f"/pdfgadd https://{Channel_url}", "").replace("?single", "")
    url = message.text.replace("/pdfgadd ", "").replace(f"{name_id}", "").replace("?single", "")
    if url == f"https://{Channel_url}" :
        print(image_url)
        # 下载图片
        r = requests.get(image_url)
        name = name_id
        id = time.strftime("%Y%m%d%H%M%S", time.localtime()) + str(random.randint(0, 100))
        extension = os.path.splitext(urllib.parse.urlparse(image_url).path)[-1].replace("jpeg", "jpg")
        with open(f'{dir_name}/{name}-{id}{extension}', 'wb') as f:
            f.write(r.content)
            bot.reply_to(message, text="添加成功，开始验证，等待30秒")
            print('添加成功，开始验证')
            sousuo(image_url, message.reply_to_message)
    else:
        bot.reply_to(message, text="格式错误，重新添加")
        print('格式错误，重新添加')
#--------------------pdfgadd指令_结束--------------------

bot.polling()


'''
telebot.apihelper.READ_TIMEOUT = 5

def send_msg(text, id):
    try:
        bot.send_message(id, text)
    except Exception as e:
        logging.info(e)
        send_msg(text, id)
'''
