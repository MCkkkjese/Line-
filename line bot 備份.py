from flask import Flask, request, abort
import traceback   # ✅ 保留，以防除錯時有用
import json

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,        # ✅ 主動推播訊息
    MulticastRequest,          # ✅ 群發訊息
    TextMessage,
    ImageMessage,              # ✅ 圖片訊息
    AudioMessage,              # ✅ 音訊訊息
    VideoMessage,              # ✅ 影片訊息
    TemplateMessage,           # ✅ 樣板訊息（新增）
    ButtonsTemplate,           # ✅ 按鈕樣板（新增）
    MessageAction,             # ✅ 按鈕選項（新增）
    FlexMessage                # ✅ 新增 Flex 訊息
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

import os

# ✅ 你的 Channel Access Token（請妥善保管）
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
Line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# ✅ 設定你的公開網址（例如 ngrok 或正式網域）
BASE_URL = "https://line-bot-six-steel.vercel.app/"  # 例如 https://abc123.ngrok.io

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        Line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        # ✅ 額外補上錯誤印出，方便除錯
        app.logger.error("Webhook Error:", e)
        traceback.print_exc()
        abort(500)

    return 'OK'

@Line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        user_text = event.message.text

        # =============================
        # ✅ 新增「選單功能」邏輯
        # =============================
        if user_text == "選單":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TemplateMessage(
                            alt_text="這是樣板訊息（Buttons Template）",
                            template=ButtonsTemplate(
                                title="功能選單",
                                text="請選擇一個功能：",
                                actions=[
                                    MessageAction(label="查詢天氣", text="我要查天氣"),
                                    MessageAction(label="最新消息", text="給我最新消息"),
                                    MessageAction(label="聯絡客服", text="聯絡客服"),
                                    MessageAction(label="關於我們", text="聯絡我們")
                                ]
                            )
                        )
                    ]
                )
            )
            return  

        # =============================
        # ✅ 新增「Flex 功能」
        # 使用者輸入 NTUE → 回覆 Flex 卡片
        # =============================
        if user_text == "NTUE":
            flex_json = {
              "type": "bubble",
              "hero": {
                "type": "image",
                "url": "https://www.overseas.edu.tw/wp-content/uploads/2020/10/%E5%9C%8B%E7%AB%8B%E8%87%BA%E5%8C%97%E6%95%99%E8%82%B2%E5%A4%A7%E5%AD%B81-1024x683.jpg",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "國立臺北教育大學",
                    "weight": "bold",
                    "size": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "baseline",
                    "margin": "md",
                    "contents": [
                      {"type": "icon","size": "sm","url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"},
                      {"type": "icon","size": "sm","url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"},
                      {"type": "icon","size": "sm","url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"},
                      {"type": "icon","size": "sm","url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"},
                      {"type": "icon","size": "sm","url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"},
                      {"type": "text","text": "5.0 (超強)","size": "sm","color": "#999999","margin": "md","flex": 0}
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                      {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                          {"type": "text","text": "地址","color": "#aaaaaa","size": "md"},
                          {"type": "text","text": "106320台北市大安區和平東路二段134 號","wrap": True,"color": "#666666","size": "sm","flex": 5}
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                          {"type": "text","text": "Time","color": "#aaaaaa","size": "md","flex": 1},
                          {"type": "text","text": "星期六 休息\n星期日 休息\n星期一 09:00–17:00\n星期二 09:00–17:00\n星期三 09:00–17:00\n星期四 09:00–17:00\n星期五 09:00–17:00","wrap": True,"color": "#666666","size": "sm","flex": 5}
                        ]
                      }
                    ]
                  }
                ]
              },
              "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "button",
                    "action": {"type": "uri","label": "前往校網","uri": "https://www.ntue.edu.tw/"},
                    "position": "relative","style": "secondary","margin": "md"
                  },
                  {
                    "type": "button",
                    "action": {"type": "postback","label": "看數資系介紹","data": "我想了解數資系"},
                    "style": "primary","margin": "md"
                  }
                ]
              }
            }
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        FlexMessage(
                            alt_text="國北教介紹",
                            contents=flex_json
                        )
                    ]
                )
            )
            return  

        # =============================
        # ✅ 原本 B 程式的 Echo 功能
        # =============================
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="你說的是：" + user_text)]
            )
        )

        # =============================
        # ✅ 原本 B 程式的「多次推播」設計
        # =============================

        # 推播純文字
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text="這是主動推播的文字訊息（Push Message）")]
            )
        )

        # 推播圖片
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=user_id,
                messages=[
                    ImageMessage(
                        original_content_url=f"{BASE_URL}/static/sample.jpg",
                        preview_image_url=f"{BASE_URL}/static/sample_preview.jpg"
                    )
                ]
            )
        )

        # 推播音訊
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=user_id,
                messages=[
                    AudioMessage(
                        original_content_url=f"{BASE_URL}/static/sample.mp3",
                        duration=60000
                    )
                ]
            )
        )

        # 推播影片
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=user_id,
                messages=[
                    VideoMessage(
                        original_content_url=f"{BASE_URL}/static/sample.mp4",
                        preview_image_url=f"{BASE_URL}/static/sample_preview.jpg"
                    )
                ]
            )
        )

        # 群發訊息
        user_ids = [user_id, '@895ibvph']  # 第二個 ID 請換成你的其他帳號
        line_bot_api.multicast_with_http_info(
            MulticastRequest(
                to=user_ids,
                messages=[TextMessage(text="這是群發訊息（Multicast Message）")]
            )
        )

if __name__ == "__main__":
    app.run()
