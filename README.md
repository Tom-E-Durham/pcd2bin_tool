# pcd2bin_tool
A tool for transferring point cloud data from pcd format to bin format, and the tutorial of how to get point cloud data from rosbag to the KITTI format.

## `pcl_ros` package

The rosbag file may contain a list of point cloud data in a certain period in the format of `messages`. This package can extract the point cloud data from a rosbag file and save it in the `.pcd` format. 

```bash
rosrun pcl_ros bag_to_pcd <input_file.bag> <topic> <output_directory>
```

After using the `pcl_ros` package, a list of `.pcd` files would be created.

## Read the `pcd` file

The `pcd` file may have a header like :

```
# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z _ intensity t reflectivity ring _ ambient _ range _
SIZE 4 4 4 1 4 4 2 1 1 2 1 4 1
TYPE F F F U F U U U U U U U U
COUNT 1 1 1 4 1 1 1 1 1 1 2 1 12
WIDTH 2048
HEIGHT 128
VIEWPOINT 0 0 0 1 0 0 0
POINTS 262144
DATA binary
```

From this, we can infer the structure as follows:

- **`x, y, z`** are floats (**`F`**), so **`4`** bytes each.
- The unnamed field (**`_`**) after **`z`** is a **`U`**, which we'll assume is 1 byte, and since **`COUNT`** is **`4`**, we have 4 bytes of padding.
- **`intensity`** is a float (**`F`**), so **`4`** bytes.
- **`t`** is an unsigned type (**`U`**) with **`4`** bytes.
- **`reflectivity`** is an unsigned type (**`U`**) with **`2`** bytes.
- **`ring`** is an unsigned type (**`U`**) with **`1`** byte.
- The unnamed field (**`_`**) after **`ring`** is 1 byte, and since **`COUNT`** is **`1`**, we have 1 byte of padding.
- **`ambient`** is an unsigned type (**`U`**) with **`2`** bytes.
- The unnamed field (**`_`**) after **`ambient`** is 1 byte, and since **`COUNT`** is **`1`**, we have 1 byte of padding.
- **`range`** is an unsigned type (**`U`**) with **`4`** bytes.
- The last unnamed field (**`_`**) with **`COUNT`** **`12`** implies 12 bytes of padding.

The format of each point stored in the ‘DATA binary’ part:

| FIELDS | x | y | z | _ | intensity | t | reflectivity | ring | _ | ambient | _ | range | _ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SIZE (bytes) | 4 | 4 | 4 | 1 | 4 | 4 | 2 | 1 | 1 | 2 | 1 | 4 | 1 |
| COUNT | 1 | 1 | 1 | 4 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 12 |
| TOTAL (bytes) | 4 | 4 | 4 | 4 | 4 | 4 | 2 | 1 | 1 | 2 | 2 | 4 | 12 |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 48 |

So, each point should have a size of 48 bytes. Since we also know the total points number is 262144 shown in the header, the total size of this point cloud in binary format should be `point_size * num_points` which is 12,582,912 bytes in this example. When we try to gather the point cloud data from this `pcd` file, we only need to parse the first 12,582,912 bytes in the ‘`DATA binary`’ (sometimes, there would be more than this number and cause a discrepancy between the size of the data counted in the ‘`DATA binary`’ and the size calculated by `point_size * num_points`).

## Save the point cloud data into the KITTI (`.bin`) format

From the previous part, we can get the point cloud data as the `binary_data` from a `pcd` file and this data contains all the fields information gathered from a LiDAR. From the header, the size of each point can be calculated which is 48 in the example. The offsets of `x`, `y`, `z` and `intensity` data are 0, 4, 8 and 16, respectively. 

In a KITTI formatted point cloud, only `x`, `y`, `z` and `intensity` values are stored using 16 bytes. So the offsets of these values in the `binary_data` can be used to parse them and save to a `bin` file.

# Usage
```
python3 pcd2bin.py --input <folder/to/pcd/files> --ouput <folder/to/save/bin/files>
```
