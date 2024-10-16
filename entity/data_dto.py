class DataDTO:
    # hello
    def __init__(
        self,
        title: str,
        data_type: str,
        service: str,
        original_location: str,
        created_at: str,
        download_url: str = None,
        file_extension: str = None,
        modified_at: str = None,
        message_from: str = None,
        message_to: str = None,
        message_attachments: list[str] = None,
    ):
        self.title = title
        self.data_type = data_type
        self.service = service
        self.original_location = original_location
        self.created_at = created_at
        self.download_url = download_url
        self.file_extension = file_extension
        self.modified_at = modified_at
        self.message_from = message_from
        self.message_to = message_to
        self.message_attachments = message_attachments

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if value is not None}
