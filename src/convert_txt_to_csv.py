import argparse

import pandas as pd
import os


def main(logfile):
    parsed = {"timestamp": [], "data_size": []}
    with open(logfile, 'r') as file:
        for line in file:
            if 'sec' in line:
                _, sec, _, nanosec = line.split(' ')
                parsed["timestamp"].append(f'{sec}_{nanosec}')
            if 'data_size' in line:
                parsed["data_size"].append(int(line.split(' ')[1]))

    df = pd.DataFrame(parsed)
    # df = df.T
    df.to_csv(f'{os.path.splitext(logfile)[0]}.csv', index=False, )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process log file.')
    parser.add_argument('logfile', help='path to the log file')
    args = parser.parse_args()

    main(args.logfile)
