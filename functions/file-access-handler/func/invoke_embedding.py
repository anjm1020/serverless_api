import requests
import json
from openai import OpenAI

from entity.formatted_data import FormattedData
from entity.index_data import IndexData
from hooks.ssm_api import ParamRequest, get_parameters


def invoke_embedding(data: FormattedData) -> IndexData:
    print(f"data.title: {data.title}")
    print(f"data.content: {len(data.content)}")
    title_vector = invoke_embedding_text(data.title)

    if len(data.content) == 0 or (
        len(data.content) == 1 and not data.content[0].strip()
    ):
        return IndexData(
            formatted_data=data, title_vector=title_vector, content_vector=[]
        )

    content_vectors = [invoke_embedding_text(chunk) for chunk in data.content]
    return IndexData(
        formatted_data=data, title_vector=title_vector, content_vector=content_vectors
    )


def invoke_embedding_text(text: str):
    return _invoke_openai_embedding_text(text)


def _invoke_openai_embedding_text(text: str):
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="openai_api_key",
            key="/findy/config/openai_api_key",
            type="string",
        ),
    ]
    params = get_parameters(required_params=required_params)
    client = OpenAI(api_key=params["openai_api_key"])
    import time

    start = time.time()
    response = client.embeddings.create(input=[text], model="text-embedding-3-small")
    end = time.time()
    print(f"Embedding Time taken: {end - start} seconds")
    return response.data[0].embedding


def _invoke_customize_embedding_text(text: str):

    params = _get_embedding_params()
    EMBEDDING_HOST = params["embedding_host"]

    try:
        response = requests.post(
            url=EMBEDDING_HOST,
            json=json.dumps({"text": text}, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        print(f"response.json():{response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error invoking embedding: {e}")
        raise e


def _get_embedding_params():
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="embedding_host",
            key="/findy/config/embedding_host",
            type="string",
        ),
    ]
    return get_parameters(required_params=required_params)
