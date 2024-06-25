import argparse
import os

current_uuid_dict = {}
outpath = ""


def parse_line(line):
    global current_uuid, outpath
    tags = line.split("#")
    container_id = tags[12]
    if container_id not in current_uuid_dict:
        current_uuid_dict[container_id] = None

    if "data=flag_data is " in line:
        uuid = line.split(" ")[-1]
        print(f"IN:  {container_id}, {uuid}")
        current_uuid_dict[container_id] = uuid
    elif "data=end_flag_data is " in line:
        uuid = line.split(" ")[-1]
        print(f"OUT: {container_id}, {uuid}")
        assert current_uuid_dict[container_id] == uuid
        current_uuid_dict[container_id] = None
    elif current_uuid_dict[container_id] is not None:
        uuid = current_uuid_dict[container_id]
        log_file = os.path.join(outpath, f"{uuid}.log")
        with open(log_file, "a") as f:
            f.write(line + "\n")


def read_file(file_path):
    global current_uuid, outpath
    outpath = os.path.dirname(file_path)
    with open(file_path, "r") as file:
        for line in file:
            parse_line(line.strip())


def main():
    parser = argparse.ArgumentParser(description="Read a file line by line.")
    parser.add_argument(
        "--sysdig-path", type=str, required=True, help="Path to the file to be read"
    )

    args = parser.parse_args()

    read_file(args.sysdig_path)


if __name__ == "__main__":
    main()
