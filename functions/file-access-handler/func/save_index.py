import requests
import json
from requests.auth import HTTPBasicAuth
from entity.index_data import IndexData

from hooks.ssm_api import get_parameters, ParamRequest


def save_index(data: IndexData):

    params = get_opensearch_params()
    USERNAME = params["opensearch_username"]
    PASSWORD = params["opensearch_password"]
    INDEX_NAME = params["opensearch_index_name"]
    OPENSEARCH_HOST = params["opensearch_host"]

    auth = HTTPBasicAuth(USERNAME, PASSWORD)

    print(f"data: {data}")
    try:
        url = f"{OPENSEARCH_HOST}/{INDEX_NAME}/_doc"
        response = requests.post(
            url=url,
            auth=auth,
            json=data.to_index_format(),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
    except requests.exceptions.RequestException as e:
        raise e


def get_opensearch_params():
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="opensearch_username",
            key="/findy/config/opensearch_username",
            type="string",
        ),
        ParamRequest(
            name="opensearch_password",
            key="/findy/config/opensearch_password",
            type="string",
        ),
        ParamRequest(
            name="opensearch_index_name",
            key="/findy/config/opensearch_index_name",
            type="string",
        ),
        ParamRequest(
            name="opensearch_host",
            key="/findy/config/opensearch_host",
            type="string",
        ),
    ]
    return get_parameters(required_params=required_params)
