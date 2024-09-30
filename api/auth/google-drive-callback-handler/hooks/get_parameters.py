import json

import boto3


def get_parameters(base_dir, required_params):
    ssm = boto3.client("ssm")

    parameter_names = [f"{base_dir}/{param}" for param in required_params.keys()]

    response = ssm.get_parameters(Names=parameter_names, WithDecryption=True)

    result = {}

    for param in response["Parameters"]:
        param_name = param["Name"].replace(f"{base_dir}/", "")
        param_value = param["Value"]

        if required_params.get(param_name) == "json":
            result[param_name] = json.loads(param_value)
        else:
            result[param_name] = param_value

    missing_params = set(required_params.keys()) - set(result.keys())
    if missing_params:
        raise ValueError(f"Missing parameters: {missing_params}")

    return result
