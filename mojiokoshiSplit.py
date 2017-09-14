#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import wave
import os
import argparse

# 環境音無いなら2048 小さければ4096 大きければ8192
SPLIT_VOLUME = 2048

# 通常は441(0.01秒に一回チェック)
CHECK_FRAME = 441

class Audio:
    def __init__(self, filename):
        self.filename = filename
        self.nframe = 0 #sample数
        self.rframe = 1 #sample rate数
        self.channels = 0 #チャンネル
        self.sampwidth = 0 #sample size

    #return audio file as array of integer
    def read(self):
        #read wav file
        wav = wave.open(self.filename, "r")

        #move to head of the audio file
        wav.rewind()

        self.nframe = wav.getnframes()
        self.rframe = wav.getframerate()
        self.channels = wav.getnchannels()
        self.sampwidth = wav.getsampwidth()

        # read to buffer as binary format
        buf = wav.readframes(self.nframe)
        wav.close()

        if(self.channels == 1):
            audio_data = np.frombuffer(buf, dtype="int16")
        elif(self.channels == 2):
            audio_data = np.frombuffer(buf, dtype="int32")

        return audio_data

    def is_split(self, y, size):
        if (len(y) > size):
            return True
        return False

    def is_silence(self, iterable):
        if max(iterable) < SPLIT_VOLUME:
            return True
        else:
            return False

    def split_equal(self, y, split_num):
        segment_points = list()
        size = len(y) / split_num;
        count = 1

        while True:
            if(count==(split_num)):
                break
            segment_points.append(size*count)
            count = count + 1

        segment_points.append(len(y))
        return segment_points

    def split(self, y, time_term, slience_time_term, max_time_term):
        size = int(self.rframe * time_term) #最小分割サイズ
        silence_size = int(self.rframe * slience_time_term) #0.1s 無音の場合切る
        max_size = int(self.rframe * max_time_term)  # 最大分割サイズ

        segment_points = list()

        count = 1
        start = 0
        end = 0
        offset = 0 #segmentポイントから時間を図り始める

        print('総フレーム数：' + str(self.nframe))
        print('総時間：' + str(int(self.nframe / size)) + '秒')

        while True:
            end = end + CHECK_FRAME
            # end = start + int(count_silence + 1) * silence_size

            if not self.is_split(y[start:self.nframe], size):
                break

            if end % size == 0:
                second = end / size
                print(str(second) + '秒まで処理')

            z1 = end - start
            check_silence = int(end + silence_size)
            z2 = np.absolute(y[end:check_silence])

            if self.is_split(y[end:self.nframe], size):
                if self.is_silence(z2) | z1 > max_size:
                    segment_points.append(end + int(silence_size / 2))
                    count = count + 1

                    offset = end + int(silence_size / 2)
                    start = int(offset)
                    end = int(offset) + size
            else:
                break

        segment_points.append(len(y))

        return segment_points

    #audioの時間、単位: s
    def audio_time(self):
        return float(self.nframe/self.rframe)

    def write(self, filename, segment_points, audio_data):
        count = 0
        start = 0
        for end in segment_points:
            version = "{:05d}".format(count)
            w = wave.Wave_write(filename+"/" + filename+"-"+version+".wav")
            w.setnchannels(self.channels)
            w.setsampwidth(self.sampwidth)
            w.setframerate(self.rframe)
            w.writeframes(audio_data[int(start):int(end)])
            start = end
            w.close()
            count = count+1


def parse_args():
    parser = argparse.ArgumentParser(description='WAV ファイル分割プログラム')
    parser.add_argument('-i', action='store', dest='file_name',
                help='wavファイルを指定', required=True, type=str)

    parser.add_argument('-type', action='store', type=str, dest='type', default="equal",
                help='分割種類の選択: 等分割、無音分割(equal | optional), デフォルト: euqal')
    parser.add_argument('-n', action='store', type=int, dest='split_num', default=2,
                help='等分割の場合, 分割数を設定, デフィルト: 2')

    parser.add_argument('-t', action='store', type=float, dest='time', default=2.0,
                help='各分割ファイルの最小サイズ, 単位: 秒, デフォルト: 2.0s')
    parser.add_argument('-mt', action='store', type=float, dest='max_time', default=10.0,
                help='各分割ファイルの最大サイズ, 単位: 秒, デフォルト: 10.0s')

    parser.add_argument('-st', action='store', type=float, dest='slience_time', default=1,
                help='無音ターム, 単位: 秒, デフォルト: 1s')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    results = parser.parse_args()
    return results

try:
    #引数の解析
    args = parse_args()

    #add progress bar, time_term, 無音term
    audio = Audio(args.file_name)
    audio_data = audio.read()
    # time = audio.audio_time()

    # 格納用フォルダ作成
    dir_name = args.file_name.replace(".wav", "")
    os.mkdir(dir_name)

    if args.type == "equal":
        segment_points = audio.split_equal(audio_data, args.split_num)
    elif args.type == "optional":
        segment_points = audio.split(audio_data, args.time, args.slience_time, args.max_time)

    output = os.path.splitext(os.path.basename(args.file_name))
    # os.system("sh check.sh " + output[0])
    audio.write(output[0], segment_points, audio_data)
except:
    print ("FALSE")
    raise