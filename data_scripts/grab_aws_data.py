import os
import sys
import s3fs
import json
from pathlib import Path
from argparse import ArgumentParser
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--cred_file", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--grab_imagenet", action="store_true", required=False, default=False)
    return parser.parse_args()

def download_object(filesystem, file_name, tar_output_path):
    print(f"Downloading {file_name} to {tar_output_path}")
    filesystem.download(file_name, tar_output_path)
    return "Success"

if __name__ == '__main__':
    args = parse_args()
    CRED_PATH = args.cred_file
    OUTPUT_PATH = args.output
    TAR_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "tars")
    IMAGENET_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "imagenet_val")

    aws_creds = json.load(open(CRED_PATH, "r"))
    print(aws_creds)

    access_key_id=aws_creds["access_key_id"]
    secret_access_key=aws_creds["secret_access_key"]
    fs = s3fs.S3FileSystem(anon=False, key=access_key_id, secret=secret_access_key)
    paths = fs.ls(aws_creds["data_root"])

    tar_files = [_path for _path in paths if ".tar" in _path and not ".xz" in _path]
    tar_files.sort()
    json_files = [_path for _path in paths if ".json" in _path]
    json_files.sort()

    imagenet_val_path = [_path for _path in paths if ".xz" in _path]
    if len(imagenet_val_path) > 0:
        imagenet_val_path = imagenet_val_path[0]
    else:
        imagenet_val_path = None

    print(len(tar_files), len(json_files), imagenet_val_path)

    os.makedirs(TAR_OUTPUT_PATH, exist_ok=True)
    KEYS_TO_DOWNLOAD = []
    for tar_file, json_file in zip(tar_files, json_files):
        tar_file = Path(tar_file)
        json_file = Path(json_file)

        dest_tar_file = tar_file.name
        dest_json_file = json_file.name
        #print(dest_tar_file, dest_json_file)
        KEYS_TO_DOWNLOAD.append((tar_file, TAR_OUTPUT_PATH)) 
        #fs.download(tar_file, TAR_OUTPUT_PATH)

    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_key = {executor.submit(download_object, fs, key[0], key[1]): key[0] for key in KEYS_TO_DOWNLOAD}

        for future in futures.as_completed(future_to_key):
            key = future_to_key[future]
            exception = future.exception()

            if not exception:
                result = future.result()
            else:
                result = exception
            
            print(f"{key} result: {result}")

    if args.grab_imagenet:
        assert not imagenet_val_path is None, "Could not find a tar.xz file!"
        fs.download(imagenet_val_path, IMAGENET_OUTPUT_PATH)