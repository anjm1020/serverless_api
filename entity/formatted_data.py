class FormattedData:
    # For Indexing Queue
    # If you have to add more properties, you can add them here.
    # Add Property Process
    # 1. Add Property @property getter
    # 2. Add Property to __init__
    # 3. Make appropriate changes in to_dict and from_dict methods
    # 4. Make appropriate changes in the constructor

    @property
    def title(self):
        return self._title

    @property
    def type(self):
        return self._type

    @property
    def original_location(self):
        return self._original_location

    @property
    def created_at(self):
        return self._created_at

    #######################################
    # for File Data
    @property
    def file_download_link(self):
        return self._file_download_link

    @property
    def file_updated_at(self):
        return self._file_updated_at

    @property
    def file_original_url(self):
        return self._file_original_url

    @property
    def file_extension(self):
        return self._file_extension

    #######################################
    # for Message Data (DM, Mail)
    @property
    def message_from(self):
        return self._message_from

    @property
    def message_to(self):
        return self._message_to

    #######################################
    # for processable Data
    @property
    def content(self):
        return self._content

    @classmethod
    def common_properties(cls, title, type, created_at, original_location):
        return cls(
            title=title,
            type=type,
            created_at=created_at,
            original_location=original_location,
        )

    @classmethod
    def non_processable_data(
        cls,
        title,
        type,
        created_at,
        original_location,
        file_updated_at,
        file_original_url,
        file_download_link,
        file_extension,
    ):
        base = cls.common_properties(
            title=title,
            type=type,
            created_at=created_at,
            original_location=original_location,
        )
        base._file_updated_at = file_updated_at
        base._file_original_url = file_original_url
        base._file_download_link = file_download_link
        base._file_extension = file_extension
        return base

    def to_dict(self):
        data = {
            "title": self.title,
            "type": self.type,
            "original_location": self.original_location,
            "created_at": self.created_at,
        }

        if self.file_original_url is not None:
            data["file_original_url"] = self.file_original_url
        if self.file_updated_at is not None:
            data["file_updated_at"] = self.file_updated_at
        if self.file_download_link is not None:
            data["file_download_link"] = self.file_download_link
        if self.file_extension is not None:
            data["file_extension"] = self.file_extension
        if self.content is not None:
            data["content"] = self.content
        if self.message_from is not None:
            data["message_from"] = self.message_from
        if self.message_to is not None:
            data["message_to"] = self.message_to

        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title"),
            type=data.get("type"),
            original_location=data.get("original_location"),
            created_at=data.get("created_at"),
            file_updated_at=data.get("file_updated_at"),
            file_original_url=data.get("original_url"),
            file_download_link=data.get("file_download_link"),
            file_extension=data.get("file_extension"),
            message_from=data.get("message_from"),
            message_to=data.get("message_to"),
            content=data.get("content"),
        )

    def __init__(
        self,
        title,
        type,
        created_at,
        original_location,
        file_original_url=None,
        file_updated_at=None,
        file_download_link=None,
        file_extension=None,
        content=None,
        message_from=None,
        message_to=None,
    ):
        self._title = title
        self._type = type
        self._original_location = original_location
        self._created_at = created_at

        self._file_original_url = file_original_url
        self._file_updated_at = file_updated_at
        self._file_download_link = file_download_link
        self._file_extension = file_extension
        self._content = content
        self._message_from = message_from
        self._message_to = message_to
