# -*- coding: utf-8 -*-
"""Google Cloud Speech API sample application using the REST API for batch
processing."""

import argparse
import base64
import json
import codecs
import os
import sys
import io

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

GOOGLE_APPLICATION_CREDENTIALS = 'hoge'

# デフォルト文字コードをutf8に変更
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')


def parse_args():
    parser = argparse.ArgumentParser(description='WAV ファイル分割プログラム')
    parser.add_argument('-i', action='store', dest='file_name',
                help='wavファイルを指定', required=True, type=str)

    parser.add_argument('-n', action='store', type=int, dest='split_num', default=1,
                help='ファイル数を設定, デフィルト: 1')

    results = parser.parse_args()
    return results


def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build(
        'speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)


def write_down(speech_file):
    """Transcribe the given audio file.

    Args:
        speech_file: the name of the audio file.
    """
    # The name of the audio file to transcribe

#    speech_file = os.path.join(
#        os.path.dirname(__file__),
#        speech_file)

#    speech_file = speech_file.replace("/", "\\")

    with io.open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    service = get_speech_service()
    service_request = service.speech().syncrecognize(
        body={
            'config': {
                'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
                'sampleRate': 44100,  # 16 khz
                'languageCode': 'ja-JP',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    response = service_request.execute()
    f = codecs.open(args.file_name + '_text.txt', 'a', 'utf-8')  # 書き込みモードで開く
    f.write(json.dumps(response, ensure_ascii=False))  # 引数の文字列をファイルに書き込む
    f.close()  # ファイルを閉じる
    print(json.dumps(response, ensure_ascii=False))


if __name__ == '__main__':
    args = parse_args()
    VOICE_REC_PATH = './' + args.file_name + '/' + args.file_name
    FILE_NUM = args.split_num + 1

    for file_number in range(FILE_NUM):
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
        write_down(voice_file)
