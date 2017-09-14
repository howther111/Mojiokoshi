#!/usr/bin/env python
# coding: UTF-8
import requests
import os
import argparse
import numpy as np
import time
import wave

GOOGLE_APIKEY = 'AIzaSyAI2lg0FPozbJCPp8qGumAObRMJw58m5aw'
VOICE_REC_PATH = ''
FILE_NUM = 1
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

    if SILENT_CHECK:
        voice_file = VOICE_REC_PATH + file_num_str + '.wav'
        print(voice_file + ' recognizing...')
        f = open(voice_file, 'rb')
        voice = f.read()
        f.close()

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

    url = 'https://www.google.com/speech-api/v2/recognize?xjerr=1&client=chromium&'\
        'lang=ja-JP&maxresults=10&pfilter=0&xjerr=1&key=' + GOOGLE_APIKEY  
    hds = {'Content-type': 'audio/l16; rate=44100'}
    
    try:    
        reply = requests.post(url, data=voice, headers=hds).text
    except IOError:
        return '#CONN_ERR'
    except:
        return '#ERROR'
        
    print('results:', reply)
    objs = reply.split(os.linesep)

    for obj in objs:
        if not obj:
            continue

        obj = obj.replace('{"result":[]}\n{"result":[{"alternative":[{"transcript":"', '')
        index = obj.find('","confidence"')  # indexは1(2文字目)
        obj = obj[0:index]
        index = obj.find('"},{"transcript"')
        obj = obj[0:index]

        if len(obj) == 0:
            continue
        return obj
    return ""


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
    FILE_NUM = args.split_num

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
                if message.find('<!DOCTYPE html>') != -1:
                    message = message + '\n'
                message = '※サーバーエラー：' + str(file_number) + '\n'
                print('your words:' + message)
            else:
                message = '\n'
                print('your words: no message')

        # sample.txtが存在しない場合は、自動的に新規作成される。
        writer = open('answer.txt', 'a')

        # テキストファイルへの書き込み
        writer.write(message)

        # 移動中のデータをクリア
        writer.flush()

        # テキストファイルとの接続を切る
        writer.close()

        # time.sleep(1)
