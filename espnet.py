# NOTE: pip shows imcompatible errors due to preinstalled libraries but you do not need to care
# !pip install -q espnet==0.10.0
# !pip install -q espnet_model_zoo



#@title Choose Japanese ASR model { run: "auto" }

lang = 'ja'
fs = 24000 #@param {type:"integer"}
tag = 'Shinji Watanabe/laborotv_asr_train_asr_conformer2_latest33_raw_char_sp_valid.acc.ave' #@param ["Shinji Watanabe/laborotv_asr_train_asr_conformer2_latest33_raw_char_sp_valid.acc.ave"] {type:"string"}


import time
import torch
import string
from espnet_model_zoo.downloader import ModelDownloader
from espnet2.bin.asr_inference import Speech2Text


d = ModelDownloader()
# It may takes a while to download and build models
speech2text = Speech2Text(
    **d.download_and_unpack(tag),
    device="cuda",
    minlenratio=0.0,
    maxlenratio=0.0,
    ctc_weight=0.3,
    beam_size=10,
    batch_size=0,
    nbest=1
)

def text_normalizer(text):
    text = text.upper()
    return text.translate(str.maketrans('', '', string.punctuation))











import pandas as pd
import soundfile
import librosa.display
from IPython.display import display, Audio
import matplotlib.pyplot as plt


from gtts import gTTS
from pydub import AudioSegment

def convert_text_voice(text):
  """
  textを受け取って、mp3の音声データに変換する関数
  """
  tts = gTTS(text, lang='ja')
  tts.save('hello.mp3')

  # convert wav to mp3                                                            
  audSeg = AudioSegment.from_mp3("hello.mp3")
  audSeg.export("hello.wav", format="wav")

!rm hello.mp3
!rm hello.wav
convert_text_voice("今日もいい天気") #変換可能

import soundfile
sp, ra = soundfile.read('/content/hello.wav', dtype='float32')from gtts import gTTS
from pydub import AudioSegment

def convert_text_voice(text):
  """
  textを受け取って、mp3の音声データに変換する関数
  """
  tts = gTTS(text, lang='ja')
  tts.save('hello.mp3')

  # convert wav to mp3                                                            
  audSeg = AudioSegment.from_mp3("hello.mp3")
  audSeg.export("hello.wav", format="wav")

!rm hello.mp3
!rm hello.wav
convert_text_voice("今日もいい天気") #変換可能

import soundfile
sp, ra = soundfile.read('/content/hello.wav', dtype='float32')





from IPython.display import display, Audio
import soundfile
import librosa.display
import matplotlib.pyplot as plt

# uploaded = files.upload()

# for file_name in uploaded.keys():

file_name = "/content/hello.wav"

speech, rate = soundfile.read(file_name)
assert rate == fs, "mismatch in sampling rate"
nbests = speech2text(speech)
text, *_ = nbests[0]

print(f"Input Speech: {file_name}")
display(Audio(speech, rate=rate))
librosa.display.waveplot(speech, sr=rate)
plt.show()
print(f"ASR hypothesis: {text_normalizer(text)}")
print("*" * 50)