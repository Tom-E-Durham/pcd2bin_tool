import struct
import os
import numpy as np
import argparse
from tqdm import tqdm

# Function to read the PCD file header and the binary point data
def read_pcd(pcd_path): # output header and the binary data, as well as point_size (step)
    header = {}
    data_start = 0 # set a val to count the length of header
    with open(pcd_path, 'rb') as f:
        while True:
            line = f.readline()
            data_start += len(line)
            if line.startswith(b'#') or len(line) == 0:
                continue
            if line.startswith(b'DATA'):
                break
            line = line.strip().decode('utf-8')
            key, value = line.split(' ', 1)
            header[key] = value
        point_size = sum(int(size) * int(count) for size, count in zip(header['SIZE'].split(), header['COUNT'].split()))
        num_points = int(header['POINTS'])
        # Read the rest of the file (binary data)
        binary_data = f.read(point_size * num_points)

    return header, point_size, binary_data


# Function to convert PCD to KITTI .bin format
def pcd_to_kitti_bin(input_pcd_path, output_bin_path):
    header, point_size, binary_data = read_pcd(input_pcd_path)
    num_points = int(header['POINTS'])

    points = []  # List to hold the point data (x, y, z, intensity)
    # Process the binary data
    for i in range(num_points):
        offset = i * point_size  # Calculate the offset for the current point
        point_data = binary_data[offset:offset+point_size]
        x, y, z = struct.unpack_from('fff', point_data, 0)
        intensity = struct.unpack_from('f', point_data, 16)
        points.append((x, y, z, intensity[0]))  # intensity is a tuple, get the first element

    # Now we can save the points to a .bin file
    with open(output_bin_path, 'wb') as bin_file:
        for point in points:
            bin_file.write(struct.pack('ffff', *point))

def main():
    parser = argparse.ArgumentParser(
        description="A tool to transfer pcd file into bin format."
    )
    parser.add_argument(
        '--input',
        type=str,
        default='Inputs',
        help='Input directory of the folder containning pcd files.')
    parser.add_argument(
        '--output',
        type=str,
        default='Outputs',
        help='Output directory of the folder containning bin files.')
    args = parser.parse_args()

    # Paths for the input PCD and output .bin file
    input_pcd_path = args.input
    output_bin_path = args.output
    # Check if the path exists
    if not os.path.exists(input_pcd_path):
        print(f"The directory {input_pcd_path} does not exist.")

    # Check if the path is a directory
    elif not os.path.isdir(input_pcd_path):
        print(f"The path {input_pcd_path} is not a directory.")

    else:
        if not os.path.exists(output_bin_path):
            print(f"The directory {input_pcd_path} does not exist.")
            os.makedirs(output_bin_path)
            print(f"The output directory {output_bin_path} was created.")

        # Get all .pcd files
        pcd_files = [f for f in os.listdir(input_pcd_path) if f.endswith('.pcd')]
    # Iterate over all files in the directory
        for filename in tqdm(pcd_files, desc="Processing PCD files"):
            if filename.endswith(".pcd"):
                file_path = os.path.join(input_pcd_path, filename)
                output_file_name = os.path.splitext(filename)[0] + '.bin'
                output_file_path = os.path.join(output_bin_path, output_file_name)
                pcd_to_kitti_bin(file_path, output_file_path)

if __name__ == '__main__':
    main()


