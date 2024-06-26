import os
import json
import pydot


def convert_svg(dot_file, svg_file):
    (graph,) = pydot.graph_from_dot_file(dot_file)
    graph.write_svg(svg_file)


def read_metadata(directory):
    metadata_path = os.path.join(directory, "metadata.json")

    # Check if the file exists
    if not os.path.exists(metadata_path):
        print(f"Error: metadata.json not found in {directory}")
        return None
    try:
        with open(metadata_path, "r") as file:
            metadata = json.load(file)
        print(f"Successfully read metadata.json from {directory}")
        return metadata
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {metadata_path}")
        return None
    except IOError:
        print(f"Error: Unable to read {metadata_path}")
        return None


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Directory {directory} created.")
    else:
        print(f"Directory {directory} already exists.")


import subprocess


def run_build(dir: str, uuid: str):
    command = [
        "go",
        "run",
        "main.go",
        "graph",
        os.path.join("../", dir, "sysdig", f"{uuid}.log"),
        os.path.join("../", dir, "net", f"{uuid}.log"),
        "remove_all",
    ]

    try:
        # Run the command
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd="./erinyes-code"
        )

        # Print the output
        print("Command output:", result.stdout)
        print("Command error (if any):", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{e.cmd}' returned non-zero exit status {e.returncode}")
        print("Error output:", e.stderr)


import subprocess


def run_dot(dotpath: str):
    # go run main.go dot ../output/leak-20240625230313/outputa.dot
    command = [
        "go",
        "run",
        "main.go",
        "dot",
        os.path.join("../", dot_path),
        # "../output/leak-20240625230313/sysdig/5de98637-66c0-4ed6-bbb0-09050b2cfd0e.log",
        # "../output/leak-20240625230313/net/5de98637-66c0-4ed6-bbb0-09050b2cfd0e.log",
    ]

    try:
        # Run the command
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd="./erinyes-code"
        )

        # Print the output
        print("Command output:", result.stdout)
        print("Command error (if any):", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{e.cmd}' returned non-zero exit status {e.returncode}")
        print("Error output:", e.stderr)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: python generate-dot.py ./output/leak-20240625230313")
        sys.exit(1)

    directory = sys.argv[1]
    directory = directory.lstrip("./")
    metadata = read_metadata(directory)

    dot_base = os.path.join(directory, "dot")
    svg_base = os.path.join(directory, "svg")
    for uuid, info in metadata.items():
        data_type = info["type"]
        dot_type_base = os.path.join(dot_base, data_type)
        svg_type_base = os.path.join(svg_base, data_type)
        ensure_dir(dot_type_base)
        ensure_dir(svg_type_base)
        dot_path = os.path.join(dot_type_base, f"{uuid}.dot")
        run_build(directory, uuid)
        run_dot(dot_path)
        svg_path = os.path.join(svg_type_base, f"{uuid}.svg")
        convert_svg(dot_path, svg_path)
