# compare_topic_echo

## How to Use

The following command compares the contents of the csv file output by the `ros2 topic echo --csv --full-length [TOPIC_NAME]`:

```python
python3 src/compare_points_data.py -b [BEFORE_CSV_PATH] -a [AFTER_CSV_PATH]
```

## NOTE

- Currently only point cloud comparisons are supported.
- If the number of point clouds is large, the command will take some time to complete.
