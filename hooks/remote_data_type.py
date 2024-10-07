class ProcessableData:

    def __init__(self, user_id, service_type, credential, download_url):
        self._user_id = user_id
        self._service_type = service_type
        self._credential = credential
        self._download_url = download_url

    @property
    def user_id(self):
        return self._user_id

    @property
    def service_type(self):
        return self._service_type

    @property
    def credential(self):
        return self._credential

    @property
    def download_url(self):
        return self._download_url
