import base64


def _encode_string(v: str):
    return base64.b64encode(v.encode("utf-8")).decode("utf-8")


def _decode_string(v: str):
    if _isBase64(v):
        return base64.b64decode(v).decode("utf-8")
    return v


def encode_dict(data: dict):
    return {
        k: (
            encode_dict(v)
            if isinstance(v, dict)
            else _encode_string(v) if isinstance(v, str) else v
        )
        for k, v in data.items()
    }


def decode_dict(data: dict):
    return {
        k: (
            decode_dict(v)
            if isinstance(v, dict)
            else _decode_string(v) if isinstance(v, str) else v
        )
        for k, v in data.items()
    }


def _isBase64(str):
    try:
        base64.b64decode(str).decode("utf-8")
        return True
    except Exception:
        return False
