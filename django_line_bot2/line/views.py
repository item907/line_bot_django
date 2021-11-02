from django.shortcuts import render

# Create your views here.
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
import requests
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.cElementTree as ET
from line.models import *
import random

logger = logging.getLogger('django')

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

invoice_flag = False
chat_flag = False

@csrf_exempt
@require_POST
def webhook(request: HttpRequest):
    signature = request.headers["X-Line-Signature"]
    body = request.body.decode()

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        messages = (
            "Invalid signature. Please check your channel access token/channel secret."
        )
        logger.error(messages)
        return HttpResponseBadRequest(messages)
    return HttpResponse("OK")

@handler.add(event = MessageEvent, message = TextMessage)
def handle_message(event: MessageEvent):
    #-->1.此段不能有2個以上的if，不然會出現500 internet server error，即使該功能可以正常運作
    #   2.機器人不能連用兩個以上的reply_message，會只有回傳第一個，其餘會出現500 internet server error
    #   3.請注意全域變數及區域變數的使用
    #   4.機器人功能撰寫請放在後面，以避免if else因判斷先後順序，造成程式功能無法正常運作

    global invoice_flag
    global chat_flag
    mtext = event.message.text
    mtext.strip()
    if mtext == '@本期發票中獎號碼':
        try:
            message = monoNum(0)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤!'))

    elif mtext == '@前期發票中獎號碼':
        try:
            message = monoNum(1) + '\n\n'
            message += monoNum(2)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤!'))

    elif mtext == '@發票對獎':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請輸入發票號碼進行對獎'))
        invoice_flag = True

    elif invoice_flag == True and mtext == '@結束發票對獎':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '已結束兌獎'))
        invoice_flag = False

    elif mtext == '@狀態':
        if invoice_flag == True:
            status_i = '開啟'
        else:
            status_i = '關閉'
        if chat_flag == True:
            status_c = '開啟'
        else:
            status_c = '關閉'
        message = TextSendMessage(
            text = '發票對獎功能：' + status_i +
                   '\n聊天功能：' + status_c)

        line_bot_api.reply_message(event.reply_token, message)

    elif mtext == '@機器人你會什麼':
        message = []
        msg1 = TextSendMessage(text = '我會--' +
            '\n1.@本期發票中獎號碼' +
            '\n2.@前期發票中獎號碼--顯示前1期及前2期發票中獎號碼' +
            '\n3.@發票對獎' +
            '\n4.@結束發票對獎' +
            '\n5.@聊天開啟' +
            '\n6.@聊天關閉' +
            '\n7.@學習:你好:歡迎光臨' +
            '\n8.@刪除:你好:歡迎光臨' +
            '\n9.@更新:你好:歡迎光臨:welcome' +
            '\n10.@圖戰:發哥表示:https://i.imgur.com/LBIRTT4.jpg' +
            '\n11.@刪圖:發哥表示:https://i.imgur.com/LBIRTT4.jpg' +
            '\n12.@狀態--顯示當前狀態')
        message.append(msg1)
        line_bot_api.reply_message(event.reply_token, message)

    elif mtext == '@聊天開啟':
        chat_flag = True
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '好喔，開始聊天'))

    elif mtext == '@聊天關閉':
        chat_flag = False
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '關閉聊天'))

    #發票對獎
    elif invoice_flag == True:
        if mtext.isdigit() and len(mtext) == 8:
            try:
                content = requests.get('http://invoice.etax.nat.gov.tw/invoice.xml')
                tree = ET.fromstring(content.text)
                items = list(tree.iter(tag = 'item'))
                ptext = items[0][2].text
                temlist = ptext.split('</p>')
                t_sp = temlist[0][-8:]  #特別獎
                t_s = temlist[1][-8:]  #特獎
                tt = temlist[2].split('、')
                t_h = [tt[0][-8:], tt[1], tt[2]]  #頭獎
                tt1 = temlist[3].split('、')
                t_six = []  #增開六獎
                for i in range(len(tt1)):
                    if i == 0:
                        t_six.append(tt1[i][-3:])
                    else:
                        t_six.append(tt1[i])

                message = []
                bonus_get = False
                if mtext == t_sp:
                    msg = TextSendMessage(text = '恭喜對中特別獎!')
                    message.append(msg)
                    bonus_get = True

                if mtext == t_s:
                    msg = TextSendMessage(text = '恭喜對中特獎!')
                    message.append(msg)
                    bonus_get = True

                for t_h1 in t_h:
                    if mtext == t_h1:
                        msg = TextSendMessage(text = '恭喜對中頭獎!')
                        message.append(msg)
                        bonus_get = True
                        break
                    elif mtext[1:] == t_h1[1:]:
                        msg = TextSendMessage(text = '恭喜對中二獎!')
                        message.append(msg)
                        bonus_get = True
                        break
                    elif mtext[2:] == t_h1[2:]:
                        msg = TextSendMessage(text = '恭喜對中三獎!')
                        message.append(msg)
                        bonus_get = True
                        break
                    elif mtext[3:] == t_h1[3:]:
                        msg = TextSendMessage(text = '恭喜對中四獎!')
                        message.append(msg)
                        bonus_get = True
                        break
                    elif mtext[4:] == t_h1[4:]:
                        msg = TextSendMessage(text = '恭喜對中五獎!')
                        message.append(msg)
                        bonus_get = True
                        break
                    elif mtext[5:] == t_h1[5:]:
                        msg = TextSendMessage(text = '恭喜對中六獎!')
                        message.append(msg)
                        bonus_get = True
                        break
            
                if bonus_get == False:
                    for t_six1 in t_six:
                        if mtext[5:] == t_six1:
                            msg = TextSendMessage(text = '恭喜對中六獎!')
                            message.append(msg)
                            bonus_get = True
                            break
 
                #表示都沒中
                if bonus_get == False:
                    msg = TextSendMessage(text = '沒中獎')
                    message.append(msg)
                
                msg = TextSendMessage(text = '請繼續輸入發票號碼進行對獎')
                message.append(msg)
                line_bot_api.reply_message(event.reply_token, message)
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤'))
        else:
            message = TextSendMessage(
                text = '發票號碼輸入錯誤，請重新輸入一次' +
                       '\n結束發票對獎請輸入:@結束發票對獎')
            line_bot_api.reply_message(event.reply_token, message)

    #學習新詞
    elif mtext[:3] == '@學習':
        msg = mtext.split(':')
        if msg[1][0] == '@':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '關鍵字不可以此開頭'))
        elif len(msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            cnt = TextChat.objects.filter(keyword = msg[1], chatword = msg[2], isword = True)
            if cnt.count() > 0:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '這個詞已經會了'))
            else:
                TextChat.objects.create(keyword = msg[1], chatword = msg[2], isword = True)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '學到新的詞了'))

    #刪除詞彙
    elif mtext[:3] == '@刪除':
        msg = mtext.split(':')
        if msg[1][0] == '@':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '不可刪除此關鍵字'))
        elif len(msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            try:
                msg_c = TextChat.objects.get(keyword = msg[1], chatword = msg[2], isword = True)
                msg_c.delete()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '忘掉這個詞了'))
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤'))

    #更新詞彙
    elif mtext[:3] == '@更新':
        msg = mtext.split(':')
        if msg[1][0] == '@':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '不可更新此關鍵字'))
        elif len(msg) != 4:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            try:
                msg_u = TextChat.objects.get(keyword = msg[1], chatword = msg[2], isword = True)
                msg_u.chatword = msg[3]
                msg_u.save()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '已更新詞彙'))
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤'))

    #學習圖片
    elif mtext[:3] == '@圖戰':
        msg = mtext.split(':', 2)  #切兩刀，避免切到網址的冒號
        if msg[1][0] == '@':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '關鍵字不可以此開頭'))
        elif len(msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            cnt = TextChat.objects.filter(keyword = msg[1], chatword = msg[2], isword = False)
            if cnt.count() > 0:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '這個圖已經有了'))
            else:
                TextChat.objects.create(keyword = msg[1], chatword = msg[2], isword = False)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '學到新的圖了'))

    #刪除圖片
    elif mtext[:3] == '@刪圖':
        msg = mtext.split(':', 2)  #切兩刀，避免切到網誌的冒號
        if msg[1][0] == '@':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '不可刪除此關鍵字'))
        elif len(msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            try:
                msg_c = TextChat.objects.get(keyword = msg[1], chatword = msg[2], isword = False)
                msg_c.delete()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '忘掉這個圖了'))
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤'))

    #撈取所有詞彙
    elif mtext[:3] == '@撈取':
        msg = mtext.split(':')
        if msg[1] != 'ApTx4869':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '密碼錯誤'))
        elif len(msg) != 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '指令錯誤'))
        else:
            try:
                msg_t = TextChat.objects.filter(keyword = msg[2])
                text = '關鍵字：' + msg[2] + '\n\n'
                for c in msg_t:
                    text += c.chatword + '\n'
                message = TextSendMessage(text = text)
                line_bot_api.reply_message(event.reply_token, message)
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '詞彙撈取失敗'))

    #自動回應
    elif chat_flag == True:
        try:
            msg_f = TextChat.objects.filter(keyword = mtext)
            list_id = []
            for msg1 in msg_f:
                list_id.append(msg1.id)

            cid = random.choice(list_id)
            msg = TextChat.objects.get(id = cid)

            #判斷是文字or圖片
            if msg.isword == True:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = msg.chatword))
            else:
                #改用FlexMessage,ImageMessage無法回覆動圖
                #img_msg = ImageSendMessage(
                #    original_content_url = msg.chatword,
                #    preview_image_url = msg.chatword
                #)

                #aspect_ratio為長寬比,aspect_mode為模式
                img_msg = FlexSendMessage(
                    alt_text = "機器人回應了圖片",
                    contents = {
                        "type":"bubble",
                        "hero":{
                            "type":"image",
                            "url":msg.chatword,
                            "size":"full",
                            "aspect_ratio":"20:13",
                            "aspect_mode":"cover"
                        }
                    }
                )
                line_bot_api.reply_message(event.reply_token, img_msg)
        except:
            pass

def monoNum(n):
    content = requests.get('http://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)

    items = list(tree.iter(tag = 'item'))  #取得item標籤內容
    title = items[n][0].text  #期別
    ptext = items[n][2].text  #中獎號碼
    ptext = ptext.replace('<p>','').replace('</p>','\n')
    return title + '月\n' + ptext[:-1]  #ptext[:-1]為移除最後一個\n