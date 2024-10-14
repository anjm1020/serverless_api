from entity.formatted_data import FormattedData


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
            index_data["title"] = {
                "raw": self._formatted_data.title,
                "vectors": self._title_vector,
            }

        for field in [
            "type",
            "original_location",
            "file_original_url",
            "file_download_link",
            "file_extension",
            "message_from",
            "message_to",
        ]:
            if hasattr(self._formatted_data, field) and getattr(
                self._formatted_data, field
            ):
                index_data[field] = getattr(self._formatted_data, field)

        for date_field in ["created_at", "file_updated_at"]:
            if hasattr(self._formatted_data, date_field) and getattr(
                self._formatted_data, date_field
            ):
                index_data[date_field] = getattr(self._formatted_data, date_field)

        if (
            hasattr(self._formatted_data, "message_attachments")
            and self._formatted_data.message_attachments
        ):
            index_data["message_attachments"] = self._formatted_data.message_attachments

        index_data["chunks"] = []
        for i, chunk in enumerate(self._content_vector):
            index_data["chunks"].append(
                {"raw": self._formatted_data.content[i], "vectors": chunk}
            )
        return index_data
