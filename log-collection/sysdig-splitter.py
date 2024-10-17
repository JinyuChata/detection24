import argparse
import os

current_uuid_dict = {}
outpath = ""

fwatchdog_current_uuid_dict = {}


def parse_line(line):
    global current_uuid_dict, outpath
    tags = line.split("#")
    container_id = tags[12]
    if container_id not in current_uuid_dict:
        current_uuid_dict[container_id] = None

    if "data=flag_data is " in line:
        uuid = line.split(" ")[-1]
        # print(f"IN:  {container_id}, {uuid}")
        current_uuid_dict[container_id] = uuid
    elif "data=end_flag_data is " in line:
        uuid = line.split(" ")[-1]
        # print(f"OUT: {container_id}, {uuid}")
        # assert current_uuid_dict[container_id] == uuid
        if current_uuid_dict[container_id] != uuid:
            print(
                f"WARNING: when exit {container_id}:{uuid}, curr uuid does not match."
            )
        current_uuid_dict[container_id] = None
    elif current_uuid_dict[container_id] is not None:
        uuid = current_uuid_dict[container_id]
        log_file = os.path.join(outpath, f"{uuid}.log")
        with open(log_file, "a") as f:
            f.write(line + "\n")


def parse_fwatchdog_line(line):
    global fwatchdog_current_uuid_dict, outpath
    tags = line.split("#")
    container_id = tags[12]
    if container_id not in fwatchdog_current_uuid_dict:
        fwatchdog_current_uuid_dict[container_id] = None

    if "start_ofwatchdog_flag_data" in line:
        uuid = line.split(" ")[-1]
        # print(f"IN:  {container_id}, {uuid}")
        fwatchdog_current_uuid_dict[container_id] = uuid
    elif "end_ofwatchdog_flag_data" in line:
        uuid = line.split(" ")[-1]
        # print(f"OUT: {container_id}, {uuid}")
        if fwatchdog_current_uuid_dict[container_id] != uuid:
            print(
                f"WARNING: when exit fwatchdog {container_id}:{uuid}, curr uuid does not match."
            )
        fwatchdog_current_uuid_dict[container_id] = None
    elif fwatchdog_current_uuid_dict[container_id] is not None:
        uuid = fwatchdog_current_uuid_dict[container_id]
        log_file = os.path.join(outpath, f"{uuid}.log")
        with open(log_file, "a") as f:
            f.write(line + "\n")


def read_file(file_path):
    global current_uuid, outpath
    outpath = os.path.dirname(file_path)
    with open(file_path, "r") as file:
        for line in file:
            if "#fwatchdog#" in line:
                parse_fwatchdog_line(line.strip())
            else:
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
