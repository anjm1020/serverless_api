from entity.formatted_data import FormattedData
import unicodedata


class IndexData:

    @property
    def formatted_data(self):
        return self._formatted_data

    @property
    def title_vector(self):
        return self._title_vector

    @property
    def content_vector(self):
        return self._content_vector

    def __init__(
        self,
        formatted_data: FormattedData,
        title_vector: list[float],
        content_vector: list[float],
    ):
        self._formatted_data = formatted_data
        self._title_vector = title_vector
        self._content_vector = content_vector

    def to_dict(self):
        return {
            "formatted_data": self._formatted_data.to_dict_without_encoding(),
            "title_vector": self._title_vector,
            "content_vector": self._content_vector,
        }

    def to_index_format(self):
        index_data = {}

        if self._formatted_data.title:
            index_data["title"] = self._formatted_data.title

        if self._title_vector:
            index_data["title_vector"] = self._title_vector

        if self._content_vector:
            index_data["content"] = []
            for i, chunk in enumerate(self._content_vector):
                index_data["content"].append(
                    {"text": self._formatted_data.content[i], "vector": chunk}
                )

        for field in [
            {"field": "type", "property": "data_type"},
            {"field": "service", "property": "service"},
            {"field": "original_location", "property": "original_location"},
            {"field": "file_download_link", "property": "download_url"},
            {"field": "file_extension", "property": "file_extension"},
            {"field": "message_from", "property": "message_from"},
            {"field": "message_to", "property": "message_to"},
        ]:
            if hasattr(self._formatted_data, field["field"]) and getattr(
                self._formatted_data, field["field"]
            ):
                index_data[field["property"]] = getattr(
                    self._formatted_data, field["field"]
                )

        for date_field in ["created_at", "file_updated_at"]:
            if hasattr(self._formatted_data, date_field) and getattr(
                self._formatted_data, date_field
            ):
                index_data[date_field] = getattr(self._formatted_data, date_field)

        if (
            hasattr(self._formatted_data, "message_attachments")
            and self._formatted_data.message_attachments
        ):
            index_data["message_attachments"] = []
            for attachment in self._formatted_data.message_attachments:
                index_data["message_attachments"].append({"name": attachment})

        return encode_dict(index_data)


def encode_dict(data: dict):
    for k, v in data.items():
        if isinstance(v, str):
            data[k] = unicodedata.normalize("NFC", v)
            # data[k] = normlized.encode("utf-8").decode("utf-8")
        elif isinstance(v, dict):
            encode_dict(v)
    return data
