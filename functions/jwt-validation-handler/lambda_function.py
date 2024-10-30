from hooks.login_token import validate


def handler(event, context):
    full_token_text: str = event["headers"]["authorization"]

    token = full_token_text.split(" ")[-1]
    context = validate(token=token)

    if context is None:
        return {"isAuthorized": False}
    else:
        return {"isAuthorized": True, "context": context}
