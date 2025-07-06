import re

from src.core.errors import (
    InvalidEmail,
    InvalidUsername,
    ValidationError,
)
from src.core.result import Result


class User:
    id: int
    username: str
    email: str
    pw_hash: str | None
    is_admin: bool
    # Python 3 implicitly set __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__
    min_length: int = 3
    username_regex = re.compile(r"^[A-Za-z0-9_-]+$")

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        pw_hash: str | None,
        is_admin: bool = False,
    ):
        """Initializes a User object. Does not validate the parameters.

        Args:
            id (int): Unique identifier for the user.
            username (str): Username of the user.
            email (str): Email address of the user.
            pw_hash (str | None): Password hash of the user, or None if not set.
            is_admin (bool): Whether the user has admin privileges. Defaults to False.
        """
        self.id = id
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.is_admin = is_admin

    @classmethod
    def create(
        cls,
        id: int,
        username: str,
        email: str,
        pw_hash: str | None,
        is_admin: bool = False,
    ) -> Result["User", ValidationError]:
        """Creates a new User instance. Use this method instead of the constructor to ensure validation.

        Returns:
            Result["User", ValidationError]: The created User instance or a ValidationError.
        """
        err = cls._validate(username, email)
        if err is not None:
            return Result.Err(err)

        return Result.Ok(
            cls(
                id=id,
                username=username,
                email=email,
                pw_hash=pw_hash,
                is_admin=is_admin,
            )
        )

    # Properties expected by flask_login:
    @property
    def is_active(self):
        """Checks if the user is active.

        Returns:
            bool: Always returns True, since the User will only be created if flask_login has authorized it.
        """
        return True

    @property
    def is_authenticated(self):
        """Checks if the user is authenticated.

        Returns:
            bool: Always returns True, since the User will only be created if flask_login has authorized it.
        """
        return self.is_active

    @property
    def is_anonymous(self):
        """Checks if the user is anonymous.

        Returns:
            bool: Always returns False, since this User class will only be used for authenticated users.
        """
        return False

    def get_id(self):
        """Returns the unique identifier of the user.

        Raises:
            NotImplementedError: If the user does not have an `id` attribute.

        Returns:
            str: The unique identifier of the user as a string.
        """
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError(
                "No `id` attribute - override `get_id`"
            ) from None

    def __eq__(self, other):
        """Checks the equality of two `User` objects using `get_id`.

        Args:
            other (User): The other user to compare with.

        Raises:
            NotImplementedError: If the other object is not a `User`.

        Returns:
            bool: True if the IDs are equal, False otherwise.
        """
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        raise NotImplementedError("Cannot compare User with non-User")

    def __ne__(self, other):
        """
        Checks the inequality of two `User` objects using `get_id`.

        Args:
            other (User): The other user to compare with.

        Raises:
            NotImplementedError: If the other object is not a `User`.

        Returns:
            bool: True if the IDs are not equal, False otherwise.
        """
        if isinstance(other, User):
            return self.get_id() != other.get_id()
        raise NotImplementedError("Cannot compare User with non-User")

    @classmethod
    def _validate(cls, username: str, email: str) -> ValidationError | None:
        if cls._validate_email(email) is False:
            return InvalidEmail(email)

        if cls._validate_username(username) is False:
            return InvalidUsername(username)

    @classmethod
    def _validate_email(cls, email: str) -> bool:
        """Validates the email format.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        email_re = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

        return re.match(email_re, email) is not None

    @classmethod
    def _validate_username(cls, username: str) -> bool:
        """Validates the username format.

        Args:
            username (str): The username to validate.

        Returns:
            bool: True if the username is valid, False otherwise.
        """
        return (
            cls.min_length <= len(username)
            and cls.username_regex.match(username) is not None
        )
