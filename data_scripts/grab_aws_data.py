import os
import sys
import s3fs
import json
from pathlib import Path
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--cred_file", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    CRED_PATH = args.cred_file
    OUTPUT_PATH = args.output
    TAR_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "tars")

    aws_creds = json.load(open(CRED_PATH, "r"))
    print(aws_creds)

    access_key_id=aws_creds["access_key_id"]
    secret_access_key=aws_creds["secret_access_key"]
    fs = s3fs.S3FileSystem(anon=False, key=access_key_id, secret=secret_access_key)
    paths = fs.ls(aws_creds["data_root"])

    tar_files = [_path for _path in paths if ".tar" in _path]
    tar_files.sort()
    json_files = [_path for _path in paths if ".json" in _path]
    json_files.sort()
    print(len(tar_files), len(json_files))

    os.makedirs(TAR_OUTPUT_PATH, exist_ok=True)
    for tar_file, json_file in zip(tar_files, json_files):
        tar_file = Path(tar_file)
        json_file = Path(json_file)

        dest_tar_file = tar_file.name
        dest_json_file = json_file.name
        print(dest_tar_file, dest_json_file)
        fs.download(tar_file, TAR_OUTPUT_PATH)