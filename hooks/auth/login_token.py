import datetime

import jwt

from hooks.aws.ssm_api import ParamRequest, get_parameters

params = get_parameters(
    [
        ParamRequest(key="/oauth/jwt_key", name="jwt_key", type="str"),
        ParamRequest(key="/oauth/jwt_exp", name="jwt_exp", type="str"),
    ]
)
key = params["jwt_key"]
delta = int(params["jwt_exp"])


def issue(user_uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=delta)
    return jwt.encode(
        payload={"exp": exp, "user_uid": user_uid}, key=key, algorithm="HS256"
    )


def validate(token):
    try:
        print(f"validated token={token}")
        result = jwt.decode(token, key=key, algorithms="HS256")
    except Exception as e:
        print(f"Decode Exception : {e}")
        return None
    else:
        return result
