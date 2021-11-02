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
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
import requests
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.cElementTree as ET

logger = logging.getLogger('django')

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

invoice_flag = False

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
    global invoice_flag
    mtext = event.message.text
    if mtext == '@傳送文字':
        try:
            message = TextSendMessage(
                text = '我是LineBot，\n您好!'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@傳送圖片':
        try:
            message = ImageSendMessage(
                original_content_url = 'https://i.imgur.com/4QfKuz1.png',
                preview_image_url = 'https://i.imgur.com/4QfKuz1.png'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@傳送貼圖':
        try:
            message = StickerSendMessage(
                package_id = '1',
                sticker_id = '2'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@多項傳送':
        try:
            message = [
                StickerSendMessage(
                    package_id = '1',
                    sticker_id = '2'
                ),
                TextSendMessage(
                    text = '這是Pizza圖片!'
                ),
                ImageSendMessage(
                    original_content_url = 'https://i.imgur.com/4QfKuz1.png',
                    preview_image_url = 'https://i.imgur.com/4QfKuz1.png'
                )
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@傳送位置':
        try:
            message = LocationSendMessage(
                title = '101大樓',
                address = '台北市信義路五段7號',
                latitude = 25.034207,
                longitude = 121.564590
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@快速選單':
        try:
            message = TextSendMessage(
                text = '請選擇最喜歡的程式語言',
                quick_reply = QuickReply(
                    items = [
                        QuickReplyButton(
                            action = MessageAction(label = 'Python', text = 'Python')
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = 'Java', text = 'Java')
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = 'C#', text = 'C#')
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = 'Basic', text = 'Basic')
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤!'))

    elif mtext == '@本期中獎號碼':
        try:
            message = monoNum(0)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤!'))

    elif mtext == '@前期中獎號碼':
        try:
            message = monoNum(1) + '\n\n'
            message += monoNum(2)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤!'))

    elif mtext == '@對獎':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請輸入發票號碼進行對獎:'))
        invoice_flag = True

    elif invoice_flag == True and mtext.isdigit() and len(mtext) == 8:
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
                
            msg = TextSendMessage(text = '請繼續輸入發票號碼進行對獎:')
            message.append(msg)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤!'))

    elif invoice_flag == True and (not mtext.isdigit() or len(mtext) != 8) and mtext != '@結束對獎':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發票號碼輸入錯誤，請重新輸入一次'))

    elif invoice_flag == True and mtext == '@結束對獎':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '已結束兌獎!'))
        invoice_flag = False

    elif mtext == '@公司網站':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = 'http://www.globalesprit.com/'))

    elif mtext == '@測試網站':
        message = []
        msg = TextSendMessage(text = 'http://192.168.0.84:8000/')
        message.append(msg)
        msg = TextSendMessage(text = '外網請做VPN')
        message.append(msg)
        line_bot_api.reply_message(event.reply_token, message)

    elif mtext == '@機器人你會什麼':
        message = []
        msg1 = TextSendMessage(text = '我會--' +
            '\n1.指令：@對獎--發票對獎' +
            '\n2.指令：@結束對獎--結束發票對獎' +
            '\n3.指令：@公司網站--公司網站' +
            '\n4.指令：@測試網站--公司內部測試網站')
        message.append(msg1)
        line_bot_api.reply_message(event.reply_token, message)

def monoNum(n):
    content = requests.get('http://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)

    items = list(tree.iter(tag = 'item'))  #取得item標籤內容
    title = items[n][0].text  #期別
    ptext = items[n][2].text  #中獎號碼
    ptext = ptext.replace('<p>','').replace('</p>','\n')
    return title + '月\n' + ptext[:-1]  #ptext[:-1]為移除最後一個\n