import json

import boto3


def get_parameters(required_params):
    ssm = boto3.client("ssm")

    param_names = [p["key"] for p in required_params]

    response = ssm.get_parameters(Names=param_names, WithDecryption=True)

    result = {}

    for param in response["Parameters"]:
        param_key = param["Name"]
        param_value = param["Value"]

        for rp in required_params:
            if rp["key"] == param_key:
                param_name = rp["name"]
                if rp["type"] == "json":
                    result[param_name] = json.loads(param_value)
                else:
                    result[param_name] = param_value

    missing_params = [
        rp["name"] for rp in required_params if rp["name"] not in result.keys()
    ]
    if missing_params:
        raise ValueError(f"Missing parameters: {missing_params}")

    return result
