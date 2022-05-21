import os
from flask import Flask, request, abort, send_from_directory

from gtts import gTTS
import random, string
from pydub import AudioSegment
# import ffmpeg
import math

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, AudioSendMessage, TextSendMessage
)

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

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

@app.route('/tmp/<path:filename>')
def send_file(filename): 
    return send_from_directory('tmp', filename)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    audio_name = randomname(10)

    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    # 音声合成 → /tmpに保存
    s = gTTS(text=event.message.text, lang='ja')
    s.save(f'./tmp/{audio_name}.mp3')

    # mp3の長さ取得
    sound = AudioSegment.from_mp3(f'./tmp/{audio_name}.mp3')
    audio_duration = math.floor(sound.duration_seconds*1000)

    # mp3 -> m4a
    sound.export(f'./tmp/{audio_name}.m4a', format="ipod", codec="aac", bitrate="320K")

    line_bot_api.reply_message(
        event.reply_token,
        AudioSendMessage(
            original_content_url=f'https://yl-bot-test.herokuapp.com/tmp/{audio_name}.m4a',
            duration=audio_duration
        )
    )
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(
    #         text=f'https://yl-bot-test.herokuapp.com/tmp/{audio_name}.mp3'
    #     )
    # )

if __name__ == "__main__":
    app.run()