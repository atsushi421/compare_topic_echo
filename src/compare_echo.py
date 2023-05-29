import argparse
import os
import shutil

SEPARATED_LOG_DIR = './separated_logs'
AFTER_LOG_DIR = f'{SEPARATED_LOG_DIR}/after'
BEFORE_LOG_DIR = f'{SEPARATED_LOG_DIR}/before'


def split_log_by_message(target_log, output_dir) -> None:
    output_counter = 0
    buffer: list[str] = []

    with open(target_log, 'r') as f:
        for line in f:
            if '---' in line:
                with open(f'{output_dir}/output_{output_counter}.txt', 'w') as output_file:
                    output_file.write(''.join(buffer))
                buffer = []
                output_counter += 1
            else:
                buffer.append(line)

    # 最後のセクションを出力
    if buffer:
        with open(f'{output_dir}/output_{output_counter}.txt', 'w') as output_file:
            output_file.write(''.join(buffer))


def create_timestamp_path_map(target_dir) -> dict[str, str]:
    timestamp_path_map = {}
    for file in os.listdir(target_dir):
        file_path = os.path.join(target_dir, file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            # 3行目と4行目を結合してtimestampとする
            timestamp = lines[2].strip() + lines[3].strip()
            timestamp_path_map[timestamp] = file_path

    return timestamp_path_map


DATA_OFFSET = 24
POINT_SIZE = 16


def compare(before_map: dict[str, str], after_map: dict[str, str]) -> None:
    num_ok = 0
    num_ng = 0

    for before_ts in before_map.keys():
        if before_ts not in after_map.keys():
            continue

        with open(before_map[before_ts], 'r') as before_log, open(after_map[before_ts], 'r') as after_log:
            before_data = before_log.readlines()[DATA_OFFSET:-1]
            before_points = [
                [int(j.strip().replace('- ', ''))
                 for j in before_data[i: i + POINT_SIZE]]
                for i in range(0, len(before_data), POINT_SIZE)
            ]
            after_data = after_log.readlines()[DATA_OFFSET:-1]
            after_points = [
                [int(j.strip().replace('- ', ''))
                 for j in after_data[i: i + POINT_SIZE]]
                for i in range(0, len(after_data), POINT_SIZE)
            ]

            ng_flag = False
            num_matched = 0
            for before_point in before_points:
                if before_point in after_points:
                    num_matched += 1
                else:
                    ng_flag = True

            print("Match ratio")
            print(num_matched / len(before_points))

            if ng_flag:
                num_ng += 1
            else:
                num_ok += 1

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

    # before_log_path = "/home/atsushi22/topic_parser/logs/voxel_grid_downsample_filter/20230529_before_echo.txt"
    # after_log_path = "/home/atsushi22/topic_parser/logs/voxel_grid_downsample_filter/20230529_after2_echo.txt"

    os.mkdir(SEPARATED_LOG_DIR)
    os.mkdir(AFTER_LOG_DIR)
    os.mkdir(BEFORE_LOG_DIR)

    # それぞれのログをtxtファイルに分割
    split_log_by_message(before_log_path, BEFORE_LOG_DIR)
    split_log_by_message(after_log_path, AFTER_LOG_DIR)

    # timestampとファイルパスの辞書を作成
    before_map = create_timestamp_path_map(BEFORE_LOG_DIR)
    after_map = create_timestamp_path_map(AFTER_LOG_DIR)

    # before_mapとafter_mapを比較
    compare(before_map, after_map)

    shutil.rmtree(SEPARATED_LOG_DIR)
