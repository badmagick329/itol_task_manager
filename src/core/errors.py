class DomainError(Exception):
    """Base for all domain‐level errors."""

    pass


class InvalidEmail(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Invalid email: {email}")
        self.email = email


class UsernameTaken(DomainError):
    def __init__(self, username: str):
        super().__init__(f"Username already taken: {username}")
        self.username = username


class InvalidUsername(DomainError):
    def __init__(
        self,
        username: str,
        min_length: int = 3,
        valid_chars: str = "alphanumeric, underscores, and hyphens",
    ):
        super().__init__(
            f"Invalid username: {username}. Usernames must be at least {min_length} characters long and can only contain {valid_chars}."
        )
        self.username = username


class InvalidPassword(DomainError):
    def __init__(self, password: str, min_length: int = 8):
        super().__init__(
            f"Invalid password: {password}. Passwords must be at least {min_length} characters long."
        )
        self.password = password


class UserCreationError(DomainError):
    def __init__(self):
        super().__init__("Error creating user. Please try again later.")


class UserNotFoundError(DomainError):
    def __init__(self, username_or_email: str):
        super().__init__(f"User not found: {username_or_email}")
        self.username_or_email = username_or_email


class PasswordsDoNotMatchError(DomainError):
    def __init__(self):
        super().__init__("Passwords do not match. Please try again.")
