# Queue Message for cred queue
class UserCredentials:

    def __init__(
        self,
        user_id,
        service_type,
        service_account,
        scopes,
        access_token,
        refresh_token,
    ):
        self._user_id = user_id
        self._service_type = service_type
        self._service_account = service_account
        self._scopes = scopes
        self._access_token = access_token
        self._refresh_token = refresh_token

    @property
    def user_id(self):
        return self._user_id

    @property
    def service_type(self):
        return self._service_type

    @property
    def service_account(self):
        return self._service_account

    @property
    def scopes(self):
        return self._scopes

    @property
    def access_token(self):
        return self._access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "service_type": self.service_type,
            "service_account": self.service_account,
            "scopes": self.scopes,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            service_type=data["service_type"],
            service_account=data["service_account"],
            scopes=data["scopes"],
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )

    def __repr__(self) -> str:
        return f"UserCredentials(user_id={self.user_id}, service_type={self.service_type}, service_account={self.service_account}, scopes={self.scopes}, access_token={self.access_token}, refresh_token={self.refresh_token})"
