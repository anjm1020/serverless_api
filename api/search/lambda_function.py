import json

import requests
from openai import OpenAI
from requests.auth import HTTPBasicAuth

from entity.data_dto import DataDTO
from hooks.aws.ssm_api import ParamRequest, get_parameters
from hooks.db.history_db import get_connection, save_history


def handler(event, context):
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_uid"]
        query = event["queryStringParameters"]["query"]

        params = _get_params()
        vector = _invoke_embedding(query, params["openai_api_key"])
        query_filters = _parse_query(query)
        result = _invoke_search_request(
            query=query, q_vector=vector, params=params, filters=query_filters
        )

        conn = get_connection(None)
        save_history(conn, query=query, user_id=user_id)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(_serialize_result(result), ensure_ascii=False),
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": str(e),
        }


def _invoke_search_request(query: str, q_vector: list[float], params: dict, filters={}):
    opensearch_username = params["opensearch_username"]
    opensearch_password = params["opensearch_password"]
    opensearch_index_name = params["opensearch_index_name"]
    opensearch_host = params["opensearch_host"]

    auth = HTTPBasicAuth(opensearch_username, opensearch_password)

    url = f"{opensearch_host}/{opensearch_index_name}/_search"

    filter_query = _get_filter_query(filters)

    query_with_knn = {
        "_source": {"excludes": ["title_vector", "content"]},
        "explain": True,
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": query}},
                    {"knn": {"title_vector": {"vector": q_vector, "min_score": 0.7}}},
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
                                        "vector": q_vector,
                                        "min_score": 0.7,
                                    }
                                }
                            },
                        }
                    },
                ],
                "minimum_should_match": 1,
                "filter": filter_query,
            },
        },
    }
    try:
        response = requests.get(url, auth=auth, json=query_with_knn)
        response.raise_for_status()
        return response.json()["hits"]["hits"]

    except Exception as e:
        print(f"Error: {e}\nError Message: {response.text}")
        raise e


def _get_filter_query(filters: dict):

    filters_list = []
    date_from = None
    date_to = None
    for key, value in filters.items():
        if key in ["data_type", "file_extension", "service"]:
            filters_list.append({"match_phrase": {key: value}})
        elif key in ["message_from", "message_to"]:
            filters_list.append({"match": {key: value}})
        elif key in ["message_attachements.name"]:
            filters_list.append(
                {
                    "nested": {
                        "path": "message_attachements",
                        "query": {"match": {"message_attachements.name": value}},
                    }
                }
            )
        elif key in ["date_from"]:
            date_from = value
        elif key in ["date_to"]:
            date_to = value
    if date_from and date_to:
        filters_list.append(
            {
                "bool": {
                    "should": [
                        {"range": {"created_at": {"gte": date_from, "lte": date_to}}},
                        {"range": {"modified_at": {"gte": date_from, "lte": date_to}}},
                    ],
                    "minimum_should_match": 1,
                }
            }
        )
    elif date_from:
        filters_list.append(
            {
                "bool": {
                    "should": [
                        {"range": {"created_at": {"gte": date_from}}},
                        {"range": {"modified_at": {"gte": date_from}}},
                    ],
                    "minimum_should_match": 1,
                }
            }
        )
    elif date_to:
        filters_list.append(
            {
                "bool": {
                    "should": [
                        {"range": {"created_at": {"lte": date_to}}},
                        {"range": {"modified_at": {"lte": date_to}}},
                    ],
                    "minimum_should_match": 1,
                }
            }
        )

    return filters_list


def _serialize_result(result: list[dict]):
    return [DataDTO(**hit["_source"]).to_dict() for hit in result]


def _parse_query(query: str):
    return {}


def _invoke_embedding(text: str, api_key: str):
    client = OpenAI(api_key=api_key)
    embedding = client.embeddings.create(input=text, model="text-embedding-3-small")
    return embedding.data[0].embedding


def _get_params():
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
    return params


if __name__ == "__main__":
    print(_get_filter_query({"date_from": "2024-01-01", "date_to": "2024-01-31"}))
