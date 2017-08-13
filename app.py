# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationMessage, LocationSendMessage,
)

app = Flask(__name__)

handler = WebhookHandler('Your_Channel_Secret') 
line_bot_api = LineBotApi('Your_Channel_Access_Token') 


@app.route('/')
def index():
    return "<p>Hello World!</p>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ================= 機器人區塊 Start =================
import random
# 接收文字訊息 ----------------------------------------
@handler.add(MessageEvent, message=TextMessage)  # default
def handle_text_message(event):                  # default
    msg = event.message.text #message from user
    # msg=input("msg=")         #input()是在terminal/cmd鍵盤輸入的，這裡是用line傳進來的

    # 針對使用者各種訊息的回覆 Start =========
    reply = ""
    
    keyword_list = ["心情不好","給個鼓勵"]
    good_list = [
                    "一個人走得快，一群人走得遠",
                    "我們也是一群會想放棄的凡人，唯一的差別是，最後我們選擇走下去"
                ]
    if msg in keyword_list:
        index = random.randint(0,len(good_list)-1)
        print(good_list[index]) #print會印在Heroku log中，不會在line出現
        reply = good_list[index]
    elif msg=="我很滿意你的服務":
        print("希望你有愉快的一天")
        reply = "希望你有愉快的一天"
    else:
        print("我聽不懂你在說什麼！")
        reply = "我聽不懂你在說什麼！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

    # 針對使用者各種訊息的回覆 End =========

# 接收位置資訊 ----------------------------------------
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    now_lat=event.message.latitude
    now_lng=event.message.longitude
    
    reply = "現在位置：緯度{},經度{}".format(now_lat,now_lng)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ================= 機器人區塊 End =================

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
