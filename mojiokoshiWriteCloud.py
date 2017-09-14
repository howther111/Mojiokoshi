#!/usr/bin/env python
# coding: UTF-8
import os
import io
import argparse
import numpy as np
import time
import wave

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

GOOGLE_APIKEY = 'AIzaSyCExgexBePYmp1sCXwIjdhK6TLXU92b0Ds'
VOICE_REC_PATH = ''
FILE_NUM = 1
# FILE_START_NUM = 0
# FILE_END_NUM = 1
SILENT_VOLUME = 14400
SILENT_CHECK = False

def recognize(file_number):

    file_num_str = ''
    if file_number < 10:
        file_num_str = '-0000' + str(file_number)
    elif file_number < 100:
        file_num_str = '-000' + str(file_number)
    elif file_number < 1000:
        file_num_str = '-00' + str(file_number)
    elif file_number < 10000:
        file_num_str = '-0' + str(file_number)
    else:
        file_num_str = '-' + str(file_number)

    voice_file = VOICE_REC_PATH + file_num_str + '.wav'
    print(voice_file + ' recognizing...')
    # f = open(voice_file, 'rb')
    # voice = f.read()
    # f.close()

    if SILENT_CHECK:
        # read wav file
        wav = wave.open(voice_file, "r")
        # move to head of the audio file
        wav.rewind()
        # read to buffer as binary format
        nframe = wav.getnframes()
        buf = wav.readframes(nframe)
        wav.close()

        channels = wav.getnchannels()
        if (channels == 1):
            audio_data = np.frombuffer(buf, dtype="int16")
        elif (channels == 2):
            audio_data = np.frombuffer(buf, dtype="int32")

        z1 = np.absolute(audio_data[0:-1])
        if is_silence(z1):
            return '#SILENT'

    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = os.path.join(
        os.path.dirname(__file__),
        voice_file)

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='ja-JP')

    # url = 'https://www.google.com/speech-api/v2/recognize?xjerr=1&client=chromium&'\
    #     'lang=ja-JP&maxresults=10&pfilter=0&xjerr=1&key=' + GOOGLE_APIKEY
    # hds = {'Content-type': 'audio/l16; rate=44100'}
    
    try:    
        reply = client.recognize(config, audio)
    except IOError:
        return '#CONN_ERR'
    except:
        return '#ERROR'
        
    print('results:', reply)
    if not reply.results:
        return '#SILENT'

    if len(reply.results) == 0:
        return '#SILENT'

    alternatives = reply.results[0].alternatives
    # objs = reply.split(os.linesep)

    for alternative in alternatives:
        if not alternative:
            continue

        message_text = str(alternative)
        message_text = message_text.replace('transcript: "', '')
        index = message_text.find('"\n,"confidence"')  # indexは1(2文字目)
        message_text = message_text[0:index]
        if not message_text.find('"},{"transcript"') == -1:
            index = message_text.find('"},{"transcript"')
            message_text = message_text[0:index]

        return message_text
    return '#SILENT'


def parse_args():
    parser = argparse.ArgumentParser(description='WAV ファイル分割プログラム')
    parser.add_argument('-i', action='store', dest='file_name',
                help='wavファイルを指定', required=True, type=str)

    parser.add_argument('-n', action='store', type=int, dest='split_num', default=1,
                help='ファイル数を設定, デフィルト: 1')

    results = parser.parse_args()
    return results


def is_silence(iterable):
    if max(iterable) < SILENT_VOLUME:
        return True
    else:
        return False


def current_milli_time():
    return int(round(time.time() * 1000))

if __name__ == '__main__':
    args = parse_args()
    VOICE_REC_PATH = './' + args.file_name + '/' + args.file_name
    FILE_NUM = args.split_num + 1

    for file_number in range(FILE_NUM):
        t0 = current_milli_time()
        message = recognize(file_number)
        print('recognized:' + str(current_milli_time() - t0) + 'ms')
        if message == '#CONN_ERR':
            print('internet not available')
            message = '※インターネットエラー：' + str(file_number) + '\n'
            print('your words:' + message)
        elif message == '#ERROR':
            print('voice recognizing failed')
            message = '※音声認識エラー：' + str(file_number) + '\n'
            print('your words:' + message)
        elif message == '#SILENT':
            print('voice is silence')
            message = '\n'
            print('your words: no message')
        else:
            if not message == '{"result":[]}':
                if message.find('<!DOCTYPE html>') == -1:
                    message = message + '\n'
                else:
                    message = '※サーバーエラー：' + str(file_number) + '\n'
                print('your words:' + message)
            else:
                message = '\n'
                print('your words: no message')

        # 自動的に新規作成されるかチェック。
        writer = open(args.file_name + '_text.txt', 'a')

        # テキストファイルへの書き込み
        writer.write(message)

        # 移動中のデータをクリア
        writer.flush()

        # テキストファイルとの接続を切る
        writer.close()

        # time.sleep(1)
