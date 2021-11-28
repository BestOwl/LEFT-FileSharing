# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import argparse
import os.path
import secrets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="test file path", required=True)
    parser.add_argument("--test-mode", type=str, help="Mode: \n[head] \n[middle] \n[tail] \n[append]", default="head")
    parser.add_argument("--test-size", type=int, help="Test size in bytes", default=10485760)  # 10MB

    args = parser.parse_args()

    total_file_size = os.path.getsize(args.path)
    print(f"File size: {total_file_size}")
    print(f"Mode: {args.test_mode}")
    print(f"Test size: {args.test_size}")

    with open(args.path, "r+b") as f:
        if args.test_mode == "head":
            f.seek(0)
        elif args.test_mode == "tail":
            f.seek(total_file_size - args.test_size)
        elif args.test_mode == "append":
            f.seek(total_file_size)

        f.write(secrets.token_bytes(args.test_size))

    print("Operation completed")


if __name__ == "__main__":
    main()
