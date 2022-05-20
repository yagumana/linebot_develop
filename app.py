import os
from flask import Flask, request, abort

import ffmpeg
from gtts import gTTS

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, AudioSendMessage,
)

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

os.mkdir('tmp')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    s = gTTS(text=event.message.text, lang='ja')
    s.save('./tmp/audio.mp3')

    line_bot_api.reply_message(
        event.reply_token,
        AudioSendMessage(
            original_content_url='https://yl-bot-test.herokuapp.com/tmp/audio.mp3',
            # original_content_url='https://dl.espressif.com/dl/audio/gs-16b-1c-44100hz.mp3',
            duration=240000
        )
    )

if __name__ == "__main__":
    app.run()