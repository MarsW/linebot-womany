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
import requests
import json
import random
place = ""
# 接收文字訊息 ----------------------------------------
@handler.add(MessageEvent, message=TextMessage)  # default
def handle_text_message(event):                  # default
    msg = event.message.text #message from user
    # msg=input("msg=")         #input()是在terminal/cmd鍵盤輸入的，這裡是用line傳進來的

    global place
    # 針對使用者各種訊息的回覆 Start =========
    reply = ""
    
    # 串接api.ai
    session_id ="COPY CURL"
    client_ac = "Client access token"

    url = "https://api.api.ai/v1/query?query={}&lang=zh-TW&sessionId={}".format(msg,session_id)
    header={
        "Authorization":"Bearer {}".format(client_ac)
    }
    rep = requests.get(url,headers=header)
    html = rep.text
    data = json.loads(html)
    intent = data['result']['metadata']['intentName']
    if intent=="Ask for help":
        place = data['result']['parameters']['POI']
        reply = data['result']['speech']
        print (place)
    else:
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
    global place
    now_lat=event.message.latitude
    now_lng=event.message.longitude
    
    if (place):
        url = "https://maps.googleapis.com/maps/api/place/search/json?location={},{}&rankby=distance&types={}&key=你的金鑰&language=zh-TW".format(now_lat,now_lng,place)
        rep = requests.get(url)
        html = rep.text
        data = json.loads(html)
        first = data['results'][0]
        title = first['name']
        print (title)
        address = first['vicinity']
        lat = first['geometry']['location']["lat"]
        lng = first['geometry']['location']["lng"]
        line_bot_api.reply_message(
            event.reply_token,
            LocationSendMessage(
                title=title, address=address,
                latitude=lat, longitude=lng
            )
        )
    else:
        reply = "我知道你現在在{}{}，但我不知道你要找什麼".format(now_lat,now_lng,place)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

# ================= 機器人區塊 End =================

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
