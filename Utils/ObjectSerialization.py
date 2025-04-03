import base64
import dataclasses
import json

from Utils.DictToDataclass import dict_to_dataclass


def data_to_base64_json_encoded_bytes(data: object) -> bytes:
    return base64.b64encode(json.dumps(dataclasses.asdict(data)).encode())

def bytes_to_object(data: bytes, data_class: any) -> any:
    data = json.loads(base64.b64decode(data.decode()))
    return dict_to_dataclass(data, data_class)
