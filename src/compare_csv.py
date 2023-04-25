import argparse

import glob
import pprint

import pandas as pd


def main(dir_path):
    before_df = pd.DataFrame()
    after_df = pd.DataFrame()

    for file in glob.glob(f'{dir_path}/**/*.csv', recursive=True):
        if 'before' in file:
            before_df = pd.read_csv(file)
        if 'after' in file:
            after_df = pd.read_csv(file)

    # Compare
    num_ok = 0
    num_ng = 0
    for _, bf_row in before_df.iterrows():
        timestamp = bf_row['timestamp']
        for _, af_row in after_df.iterrows():
            if timestamp == af_row['timestamp']:
                if bf_row['data_size'] == af_row['data_size']:
                    num_ok += 1
                else:
                    num_ng += 1
                break

    print('=== Rusult ===')
    print(f'OK: {num_ok}')
    print(f'NG: {num_ng}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process log dir.')
    parser.add_argument('dir', help='path to the log dir')
    args = parser.parse_args()

    main(args.dir)
