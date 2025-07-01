class User:
    id: int
    username: str
    email: str
    pw_hash: str | None

    def __init__(
        self, id: int, username: str, email: str, pw_hash: str | None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
