class User:
    id: int
    username: str
    email: str
    pw_hash: str | None
    is_admin: bool
    # Python 3 implicitly set __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        pw_hash: str | None,
        is_admin: bool = False,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.is_admin = is_admin

    # Properties expected by flask_login:
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError(
                "No `id` attribute - override `get_id`"
            ) from None

    def __eq__(self, other):
        """
        Checks the equality of two `User` objects using `get_id`.
        """
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `User` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal
