from django.shortcuts import render

import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

logger = logging.getLogger('django')

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

@csrf_exempt
@require_POST
def webhook(request: HttpRequest):
    signature = request.headers['X-Line-Signature']
    body = request.body.decode()

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        message = (
            "Invalid signature. Please check your channel access token/channel serect."
        )
        logger.error(messages)
        return HttpResponseBadRequest(messages)
    return HttpResponse("OK")

@handler.add(event = MessageEvent, message = TextMessage)
def handle_message(event: MessageEvent):
    #if event.source.user_id == "U9744d5a9dcc98a2c1516b891ca912e3d":
    line_bot_api.reply_message(
        reply_token = event.reply_token,
        messages = TextSendMessage(text = event.message.text),
    )