import os
from flask import Flask, request, abort, send_from_directory

from gtts import gTTS
import random, string
from pydub import AudioSegment
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

class Status:
    def __init__(self):
        self.context = '0'

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context

class MySession:
    _status_map = dict()

    def register(user_id):
        if MySession._get_status(user_id) is None:
            MySession._put_status(user_id, Status())

    def reset(user_id):
        MySession._put_status(user_id, Status())

    def _get_status(user_id):
        return MySession._status_map.get(user_id)
    
    def _put_status(user_id, status: Status):
        MySession._status_map[user_id]= status

    def read_context(user_id):
        return MySession._status_map.get(user_id).get_context()

    def update_context(user_id, context):
        new_status = MySession._status_map.get(user_id)
        new_status.set_context(context)
        MySession._status_map[user_id] = new_status

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
    input_text = event.message.text
    user_id = event.source.user_id

    MySession.register(user_id)

    if MySession.read_context(user_id) == "0":
        if input_text == "読み上げ":
            line_bot_api.reply_message(
                event.reply.token,
                TextSendMessage(
                    text="読み上げたい文章を入力してください"
                )
            )
            MySession.update_context(user_id, "1")
        elif input_text == "音声加工":
            line_bot_api.reply_message(
                event.reply.token,
                TextSendMessage(
                    text="音声加工は準備中です"
                )
            )
            MySession.reset(user_id)
        else:
            line_bot_api.reply_message(
                event.reply.token,
                TextSendMessage(
                    text="「読み上げ」か「音声加工」と入力してください]"
                )
            )
            MySession.reset(user_id)
    
    if MySession.read_context == "1":
        audio_name = randomname(10)

        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        # 音声合成 → /tmpに保存
        s = gTTS(text=input_text, lang='ja')
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
        MySession.reset(user_id)

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(
    #         text=access_counter
    #     )
    # )


if __name__ == "__main__":
    app.run()