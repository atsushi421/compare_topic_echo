import math
import struct

from tqdm import tqdm


class Point:
    def __init__(self, x: list[int], y: list[int], z: list[int], intensity: list[int]):
        def to_float(chars: list[int]) -> float:
            bytes_repr = bytes(chars)
            float_value = struct.unpack('f', bytes_repr)[0]

            return float_value

        self.x = to_float(x)
        self.y = to_float(y)
        self.z = to_float(z)
        self.intensity = to_float(intensity)

    def __eq__(self, other):
        FACTOR = 100000000.0
        dx = self.x*FACTOR - other.x*FACTOR
        dy = self.y*FACTOR - other.y*FACTOR
        dz = self.z*FACTOR - other.z*FACTOR
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        EQ_THRESHOLD = 0.001
        return distance / FACTOR < EQ_THRESHOLD and self.intensity == other.intensity


def create_timestamp_points_map(src_log_path: str) -> dict[str, list[Point]]:
    ts_points_map = {}

    with open(src_log_path, 'r') as file:
        for line in file:
            message_contents = line.strip().split(',')

            timestamp = message_contents[0] + message_contents[1]

            # Starting from the 20th column, process every 16 columns to create Point instances
            POINT_DATA_OFFSET = 20
            POINT_STEP = 16
            points = []
            for i in range(POINT_DATA_OFFSET, len(message_contents)-1, POINT_STEP):
                x = [int(message_contents[j]) for j in range(i, i+4)]
                y = [int(message_contents[j]) for j in range(i+4, i+8)]
                z = [int(message_contents[j]) for j in range(i+8, i+12)]
                intensity = [int(message_contents[j]) for j in range(i+12, i+16)]

                point = Point(x, y, z, intensity)
                points.append(point)

            ts_points_map[timestamp] = points

    return ts_points_map


if __name__ == "__main__":
    before_log_path = "/home/atsushi22/topic_parser/logs/voxel_grid_downsample_filter/before_topic_echo.csv"
    after_log_path = "/home/atsushi22/topic_parser/logs/voxel_grid_downsample_filter/after_topic_echo.csv"

    print('=== Creating timestamp points map ===')
    before_map = create_timestamp_points_map(before_log_path)
    after_map = create_timestamp_points_map(after_log_path)

    print('=== Comparing points ===')
    num_match_messages = 0
    num_not_match_messages = 0
    for before_ts in tqdm(before_map.keys()):
        if before_ts not in after_map.keys():
            continue
        assert len(before_map[before_ts]) == len(after_map[before_ts])

        not_match_flag = False
        for before_point in before_map[before_ts]:
            if any(before_point == after_point for after_point in after_map[before_ts]):
                continue
            else:
                not_match_flag = True
                break

        if not_match_flag:
            num_not_match_messages += 1
        else:
            num_match_messages += 1

    print('=== Result ===')
    print(f'Match: {num_match_messages}')
    print(f'Not match: {num_not_match_messages}')
