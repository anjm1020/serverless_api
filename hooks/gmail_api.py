import html2text
import base64

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from entity.accessible_data import AccessibleData
from entity.formatted_data import FormattedData

from hooks.ssm_api import ParamRequest, get_parameters


def get_profile(credentials: Credentials):
    try:
        print("Start get profile")
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        print(f"Response Profile: {profile}")
        return profile

    except RefreshError as e:
        print(f"Token expired or invalid: {e}")
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e


def get_mail_and_attachments_list(credentials: Credentials):
    required_params: list[ParamRequest] = [
        ParamRequest(
            name="max_mail_length",
            key="/findy/config/max_mail_length",
            type="integer",
        )
    ]
    params = get_parameters(required_params=required_params)
    max_length = int(params["max_mail_length"])

    service = build("gmail", "v1", credentials=credentials)

    pageToken = None
    mails = []
    while True:
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                pageToken=pageToken,
                maxResults=500,
                includeSpamTrash=False,
                q="in:inbox newer_than:1y",
            )
            .execute()
        )
        mails.extend(response.get("messages", []))

        if len(mails) >= max_length:
            mails = mails[:max_length]
            break

        pageToken = response.get("nextPageToken", None)
        if pageToken is None:
            break
    return mails


def segmentation(entire_list) -> tuple[list[AccessibleData], list[FormattedData]]:
    # All mail have to process
    return [AccessibleData(access_info=mail) for mail in entire_list], []


def get_mail_content(credentials: Credentials, mail_id: str) -> FormattedData:
    service = build("gmail", "v1", credentials=credentials)
    mail = service.users().messages().get(userId="me", id=mail_id).execute()

    headers = mail["payload"]["headers"]
    subject = next(
        (header["value"] for header in headers if header["name"].lower() == "subject"),
        "",
    )
    sender = next(
        (header["value"] for header in headers if header["name"].lower() == "from"), ""
    )
    recipient = next(
        (header["value"] for header in headers if header["name"].lower() == "to"), ""
    )
    date_str = next(
        (header["value"] for header in headers if header["name"].lower() == "date"), ""
    )
    created_at = FormattedData.parse_date_for_gmail(date_str)

    body_plain = ""
    body_html = ""
    attachments = []
    if "parts" in mail["payload"]:
        for part in mail["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                encoded_data = part["body"]["data"]
                body_plain = decode_text(encoded_data)
            elif part["mimeType"] == "text/html":
                encoded_data = part["body"]["data"]
                body_html = extract_text_from_html(decode_text(encoded_data))
            elif "filename" in part:
                attachments.append(part["filename"])
    elif "body" in mail["payload"]:
        encoded_data = mail["payload"]["body"]["data"]
        if mail["payload"]["mimeType"] == "text/plain":
            body_plain = decode_text(encoded_data)
        elif mail["payload"]["mimeType"] == "text/html":
            body_html = extract_text_from_html(decode_text(encoded_data))

    body = body_html if body_html else body_plain
    attachment_names = ", ".join(attachments) if attachments else None

    formatted_data = FormattedData.message_data(
        title=subject,
        type="email",
        created_at=created_at,
        original_location="gmail",
        content=body,
        message_from=sender,
        message_to=recipient,
        message_attachments=attachment_names,
    )

    print(f"Formatted Data : {formatted_data.to_dict()}")
    return formatted_data


def extract_text_from_html(html_content):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    return text_maker.handle(html_content)


def decode_text(encoded_data):
    try:
        return base64.urlsafe_b64decode(encoded_data).decode("utf-8")
    except UnicodeDecodeError:
        try:
            return base64.urlsafe_b64decode(encoded_data).decode("euc-kr")
        except UnicodeDecodeError:
            return base64.urlsafe_b64decode(encoded_data).decode(
                "utf-8", errors="ignore"
            )
