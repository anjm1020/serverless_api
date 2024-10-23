from entity.user_credentials import UserCredentials
from hooks.encoding import encode_dict, decode_dict


class AccessibleData:
    # for accessible data queue

    def __init__(
        self,
        access_info: dict,
        credentials: UserCredentials = None,
        version: str = None,
    ):
        self._access_info = access_info
        self._credentials = credentials
        self._version = version
        self._access_info = decode_dict(self._access_info)

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, value: UserCredentials):
        self._credentials = value

    @property
    def access_info(self):
        return self._access_info

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    def to_dict(self):
        return {
            "access_info": encode_dict(self.access_info),
            "credentials": self.credentials.to_dict(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            access_info=data["access_info"],
            credentials=UserCredentials.from_dict(data["credentials"]),
            version=data["version"],
        )
