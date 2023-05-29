import numpy as np
import os
import matplotlib.pyplot as plt
import math
import sys
import tqdm
import argparse


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


def create_ts_points_map(log_path) -> dict[str, list[Point]]:
    ts_points_map: dict[str, list[Point]] = {}
    ts_str = ''
    x = y = z = 0.0
    with open(log_path, 'r') as file:
        for line in file:
            if 'sec' in line:
                ts_str = line.strip()
                ts_points_map[ts_str] = []
            elif 'x:' in line:
                x = float(line.strip().replace('x: ', ''))
            elif 'y:' in line:
                y = float(line.strip().replace('y: ', ''))
            else:  # z
                z = float(line.strip().replace('z: ', ''))
                ts_points_map[ts_str].append(Point(x, y, z))

    return ts_points_map


def calc_distance(point1: Point, point2: Point, factor: float) -> float:
    dx = point1.x*factor - point2.x*factor
    dy = point1.y*factor - point2.y*factor
    dz = point1.z*factor - point2.z*factor
    return math.sqrt(dx**2 + dy**2 + dz**2)


def compare_by_plot(before_map, after_map):
    PLOT_OUTPUT_DIR = './compare_points'
    os.mkdir(PLOT_OUTPUT_DIR)

    for i, before_ts in enumerate(before_map.keys()):
        if before_ts not in after_map.keys():
            continue

        before_points = np.array([[p.x, p.y, p.z] for p in before_map[before_ts]])
        after_points = np.array([[p.x, p.y, p.z] for p in after_map[before_ts]])

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(
            before_points[:, 0],
            before_points[:, 1],
            before_points[:, 2],
            color='b', label='before')
        ax.scatter(
            after_points[:, 0],
            after_points[:, 1],
            after_points[:, 2],
            color='r', label='after')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()

        plt.savefig(f'{PLOT_OUTPUT_DIR}/{i}.png')


def compare_by_distance(before_map, after_map, ok_threshold: float) -> None:
    num_ok_msgs = 0
    num_ng_msgs = 0
    FACTOR = 100000000.0

    for before_ts in tqdm.tqdm(before_map.keys()):
        if before_ts not in after_map.keys():
            continue

        before_points = before_map[before_ts]
        after_points = after_map[before_ts]
        assert len(before_points) == len(after_points)

        num_ok_points = 0
        for before_point in before_points:
            min_distance = sys.maxsize
            for after_point in after_points:
                distance = calc_distance(before_point, after_point, FACTOR)
                if distance < min_distance:
                    min_distance = distance

            if min_distance / FACTOR < ok_threshold:
                num_ok_points += 1

        if num_ok_points == len(before_points):
            num_ok_msgs += 1
        else:
            num_ng_msgs += 1

    print(f'OK: {num_ok_msgs}, NG: {num_ng_msgs}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log paths.")
    parser.add_argument("-b", "--before_log_path", type=str, required=True,
                        help="Path to the before log.")
    parser.add_argument("-a", "--after_log_path", type=str,
                        required=True, help="Path to the after log.")
    args = parser.parse_args()
    before_log_path = args.before_log_path
    after_log_path = args.after_log_path

    before_ts_points_map = create_ts_points_map(before_log_path)
    after_ts_points_map = create_ts_points_map(after_log_path)

    print('=== Compare by distance ===')
    OK_THRESHOLD = 0.001
    print(f'OK_THRESHOLD: {OK_THRESHOLD}')
    compare_by_distance(before_ts_points_map, after_ts_points_map, OK_THRESHOLD)

    print('=== Compare by plot ===')
    compare_by_plot(before_ts_points_map, after_ts_points_map)
