import argparse


def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            for line in file:
                print(line.strip())
    except FileNotFoundError:
        print(f"The file at path {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description="Read a file line by line.")
    parser.add_argument(
        "--sysdig-path", type=str, required=True, help="Path to the file to be read"
    )

    args = parser.parse_args()

    read_file(args.sysdig_path)


if __name__ == "__main__":
    main()
