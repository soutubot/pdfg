# -*- codeing = utf-8 -*-
# @Time : 2021/6/4 18:35
# @Autor : Soutubot
# @File : pdfg-bot.py
# @Software : PyCharm
# 匯入相關套件
from PIL import Image
import requests
import time
import telebot
import os
import imagehash

session = requests.session()

#-----↓需要你修改的参数↓-----
bot = telebot.TeleBot("123456:xxxxxx") #TG BOT API
bot_nanme = "@pdfg_bot" #bot名称暂时没什么卵用
group_id = -123456 #群组白名单id
admin_id = 654321 #admin白名单id
Channel_url = 'https://t.me/xxx/' #频道链接
dir_name = './download-telegram-channel-pictures/picture_storage_path/' #本地图库位置
#-----↑需要你修改的参数↑-----


#判断消息是否为回复和图片
def if_sousuo(message):
    if message.reply_to_message is not None:  # 判断是否为回复
        if message.reply_to_message.content_type == 'photo':  # 判断回复内容是否为图片
            image_url = bot.get_file_url(message.reply_to_message.photo[-1].file_id)
            bot.reply_to(message.reply_to_message, text="正在搜索中，请等待30秒", parse_mode="MarkdownV2")
            sousuo(image_url, message.reply_to_message)
        else:
            bot.reply_to(message.reply_to_message, text="请使用指令回复一张图片，暂不支持GIF和视频")
    else:
        bot.reply_to(message, text="请使用指令回复一张图片，暂不支持GIF和视频")

#pdfg指令
@bot.message_handler(commands=['pdfg'])

def send_pdfg(message):
    print(message)
    print(message.chat.id)
    if message.chat.type == 'supergroup' and message.chat.id == group_id: #判断是否本群
        if_sousuo(message)
    elif message.chat.type == 'private' and message.chat.id == admin_id:  #判断是否admin
        if_sousuo(message)
    else:
        print('非群聊&非本群&非admin')

#---------------------

def sousuo(image_url, message):
    start = time.time()

    # 获取指定目录的文件列表
    file_list = os.listdir(dir_name)
    #print(file_list)

    #假设要对比的图片为 'phash_img'，并计算phash值
    #image_url = 'https://upload.cc/i1/2021/06/04/6EdWr4.png'
    phash_img = imagehash.phash(Image.open(requests.get(image_url, stream=True).raw))
    print(f'{image_url} - phash值 - {phash_img}')

    #计算所有本地库图片的phash，并与'phash_img'计算对比数值
    phashall_value = []
    for i in file_list :
        phash = imagehash.phash(Image.open(f'{dir_name}{i}')) #先计算所有本地库图片的phash
        value = (phash - phash_img) / len(phash.hash) ** 2 #再与'phash_img'计算对比数值
        phashall_value.append(f'{value}')
    #print(phashall_value)
    end = time.time()
    print (f'计算耗时{end - start}秒')

    #判断是否有发过
    if float(min(phashall_value)) < 0.18 : #判断是否有低于0.18数值
        img_name_OK = file_list[phashall_value.index(min(phashall_value))] #返回最小值的对应图片名
        print(f'频道发过bot提醒您：频道发过！{Channel_url}{img_name_OK.replace(".jpg","")}')
        bot.reply_to(message, text=f'频道发过bot提醒您：\n频道发过！{Channel_url}{img_name_OK.replace(".jpg","")}')
    else:
        img_name_OK = file_list[phashall_value.index(min(phashall_value))]
        print(f'未匹配到，最小值是{min(phashall_value)} | {Channel_url}{img_name_OK.replace(".jpg","")}')
        bot.reply_to(message, text='未匹配到')

bot.polling()
