###
import json

import boto3

ssm = boto3.client("ssm")


class ParamRequest:
    def __init__(self, key, name, type):
        self._key = key
        self._name = name
        self._type = type

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type


def get_parameters(required_params: list[ParamRequest]):
    global ssm
    param_names = [p.key for p in required_params]

    response = ssm.get_parameters(Names=param_names, WithDecryption=True)

    result = {}

    for param in response["Parameters"]:
        param_key = param["Name"]
        param_value = param["Value"]

        for rp in required_params:
            if rp.key == param_key:
                param_name = rp.name
                if rp.type == "json":
                    result[param_name] = json.loads(param_value)
                else:
                    result[param_name] = param_value

    missing_params = [rp.name for rp in required_params if rp.name not in result.keys()]
    if missing_params:
        raise ValueError(f"Missing parameters: {missing_params}")

    return result


###
import requests
from openai import OpenAI

# from hooks.ssm_api import get_parameters, ParamRequest
from requests.auth import HTTPBasicAuth


def search(query: str, filters={}):
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
        ParamRequest(
            name="openai_api_key",
            key="/findy/config/openai_api_key",
            type="string",
        ),
    ]
    params = get_parameters(required_params=required_params)

    opensearch_username = params["opensearch_username"]
    opensearch_password = params["opensearch_password"]
    opensearch_index_name = params["opensearch_index_name"]
    opensearch_host = params["opensearch_host"]

    openai_api_key = params["openai_api_key"]

    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(input=[query], model="text-embedding-3-small")
    vector = response.data[0].embedding

    auth = HTTPBasicAuth(opensearch_username, opensearch_password)

    url = f"{opensearch_host}/{opensearch_index_name}/_search"

    query_with_knn = {
        "_source": {"excludes": ["title_vector", "content"]},
        "explain": True,
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": query}},
                    {"knn": {"title_vector": {"vector": vector, "min_score": 0.7}}},
                    {
                        "nested": {
                            "path": "content",
                            "query": {
                                "match": {
                                    "content.text": query,
                                }
                            },
                        }
                    },
                    {
                        "nested": {
                            "path": "content",
                            "query": {
                                "knn": {
                                    "content.vector": {
                                        "vector": vector,
                                        "min_score": 0.7,
                                    }
                                }
                            },
                        }
                    },
                ],
                "minimum_should_match": 1,
                "filter": filters,
            },
        },
    }
    try:
        response = requests.get(url, auth=auth, json=query_with_knn)
        response.raise_for_status()
        print(f"2. Response with KNN")
        for hit in response.json()["hits"]["hits"]:
            print(hit["_source"])

    except Exception as e:
        print(e)
        print(response.text)


def handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")

    query = event["queryStringParameters"]["query"]
    print(f"Query: {query}")
    search(query)
    return {"statusCode": 200, "body": "Search handler"}


if __name__ == "__main__":

    def _get_filter_query(filters: dict):

        filters_list = []
        date_from = None
        date_to = None
        for key, value in filters.items():
            if key in ["data_type", "file_extension", "service"]:
                filters_list.append({"match_phrase": {key: value}})
            elif key in ["message_from", "message_to", "message_attachements.name"]:
                filters_list.append({"match": {key: value}})
            elif key in ["date_from"]:
                date_from = value
            elif key in ["date_to"]:
                date_to = value

        if date_from and date_to:
            filters_list.append(
                {"range": {"created_at": {"gte": date_from, "lte": date_to}}}
            )
        elif date_from:
            filters_list.append({"range": {"created_at": {"gte": date_from}}})
        elif date_to:
            filters_list.append({"range": {"created_at": {"lte": date_to}}})

        return filters_list

    # 테스트 케이스 1: 기본적인 필터
    filter_1 = {"data_type": "document", "file_extension": "pdf", "service": "dropbox"}

    # 테스트 케이스 2: 메시지 관련 필터
    filter_2 = {
        "message_from": "user@example.com",
        "message_to": "support@company.com",
        "message_attachements.name": "report.xlsx",
    }

    # 테스트 케이스 3: 날짜 범위 필터 (from과 to 모두 있는 경우)
    filter_3 = {"date_from": "2024-01-01 00:00:00", "date_to": "2024-03-31 23:59:59"}

    # 테스트 케이스 4: 날짜 범위 필터 (from만 있는 경우)
    filter_4 = {"date_from": "2024-01-01 00:00:00"}

    # 테스트 케이스 5: 날짜 범위 필터 (to만 있는 경우)
    filter_5 = {"date_to": "2024-12-31 23:59:59"}

    # 테스트 케이스 6: 복합 필터 (여러 타입의 필터 조합)
    filter_6 = {
        "data_type": "email",
        "service": "gmail",
        "message_from": "manager@company.com",
        "date_from": "2024-01-01 00:00:00",
        "date_to": "2024-06-30 23:59:59",
    }

    # 테스트 실행
    test_cases = [filter_1, filter_2, filter_3, filter_4, filter_5, filter_6]
    test_results = []
    for i, filters in enumerate(test_cases, 1):
        print(f"테스트 케이스 {i}:")
        print("입력:", filters)
        result = _get_filter_query(filters)
        print("결과:", result)
        print()
        test_results.append(result)

    search_filter = _get_filter_query(
        filters={
            "date_from": "2024-10-01 00:00:00",
            "date_to": "2024-10-31 23:59:59",
        }
    )
    search_filter = []
    print(f"filter: {search_filter}")
    print(search("교육", search_filter))
