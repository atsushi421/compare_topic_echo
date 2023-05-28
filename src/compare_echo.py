import argparse
import os
import shutil

SEPARATED_LOG_DIR = './separated_logs'
AFTER_LOG_DIR = f'{SEPARATED_LOG_DIR}/after'
BEFORE_LOG_DIR = f'{SEPARATED_LOG_DIR}/before'


def separate_log_to_yamls(input_file, output_dir):
    output_counter = 0
    buffer = []

    with open(input_file, 'r') as f:
        for line in f:
            # '---'が含まれる行が見つかった場合
            if '---' in line:
                # これまでの行をYAMLファイルとして出力
                with open(f'{output_dir}/output_{output_counter}.txt', 'w') as output_file:
                    output_file.write(''.join(buffer))
                # バッファとカウンタをリセット
                buffer = []
                output_counter += 1
            else:
                # '---'が含まれない行はバッファに追加
                buffer.append(line)

    # 最後のセクションを出力
    if buffer:
        with open(f'{output_dir}/output_{output_counter}.txt', 'w') as output_file:
            output_file.write(''.join(buffer))


def create_timestamp_path_map(target_dir):
    timestamp_path_map = {}
    # target_dir内の全.txtファイルでループ
    for file in os.listdir(target_dir):
        file_path = os.path.join(target_dir, file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            # 3行目と4行目を結合してtimestampとする
            timestamp = lines[2].strip() + lines[3].strip()
            # timestampとファイルパスを辞書に保存
            timestamp_path_map[timestamp] = file_path
    return timestamp_path_map


def check_and_print(before_map, after_map):
    num_ok = 0
    num_ng = 0

    # before_mapの全キーでループ
    for before_ts in before_map.keys():
        # キーがafter_mapに存在する場合
        if before_ts in after_map.keys():
            before_log_path = before_map[before_ts]
            after_log_path = after_map[before_ts]
            with open(before_log_path, 'r') as before_log, open(after_log_path, 'r') as after_log:
                before_data = before_log.readlines()[23:]
                after_data = after_log.readlines()[23:]
                if before_data == after_data:
                    num_ok += 1
                else:
                    num_ng += 1

    print('=== Result ===')
    print(f'OK: {num_ok}')
    print(f'NG: {num_ng}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log paths.")
    parser.add_argument("-b", "--before_log_path", type=str, required=True,
                        help="Path to the before log.")
    parser.add_argument("-a", "--after_log_path", type=str,
                        required=True, help="Path to the after log.")

    args = parser.parse_args()

    before_log_path = args.before_log_path
    after_log_path = args.after_log_path

    os.mkdir(SEPARATED_LOG_DIR)
    os.mkdir(AFTER_LOG_DIR)
    os.mkdir(BEFORE_LOG_DIR)

    # それぞれのログをYAMLファイルに分割
    separate_log_to_yamls(before_log_path, BEFORE_LOG_DIR)
    separate_log_to_yamls(after_log_path, AFTER_LOG_DIR)

    # timestampとファイルパスの辞書を作成
    before_map = create_timestamp_path_map(BEFORE_LOG_DIR)
    after_map = create_timestamp_path_map(AFTER_LOG_DIR)

    # before_mapとafter_mapを比較
    check_and_print(before_map, after_map)

    shutil.rmtree(SEPARATED_LOG_DIR)
