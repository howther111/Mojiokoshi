import argparse

NUMBER_DISP = False

def parse_args():
    parser = argparse.ArgumentParser(description='WAV ファイル分割プログラム')
    parser.add_argument('-i', action='store', dest='file_name',
                help='txtファイルを指定', required=True, type=str)

    results = parser.parse_args()
    return results

if __name__ == '__main__':
    args = parse_args()
    TEXT_PATH = './' + args.file_name + '_text.txt'
    f = open(TEXT_PATH, 'r', encoding='utf-8')  # 'r' は読み取りモード
    input_str = f.read()  # readline を使うと1行ずつ読み込める
    f.close()
    print(input_str)

    str_list = input_str.split("    ")
    output_str = ""
    for listed_str in str_list:
        if not NUMBER_DISP:
            new_str = listed_str[:-7] + "\n"
        else:
            new_str = listed_str + "\n"
        output_str = output_str + new_str

    NEW_TEXT_PATH = './' + args.file_name + '_finish.txt'

    write_file = NEW_TEXT_PATH
    f = open(write_file, 'a', encoding='utf-8')  # 'a' は追記
    f.write(output_str)
    f.close()
