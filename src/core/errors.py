# =============================================================================
# Base Exception Classes
# =============================================================================


class DomainError(Exception):
    """Base for all domain‐level business logic errors."""

    pass


class ValidationError(Exception):
    """Base for all input validation errors."""

    pass


class InfrastructureError(Exception):
    """Base for all infrastructure-level errors (DB, external services, etc.)."""

    pass


class AuthenticationError(Exception):
    """Base for all authentication-related errors (who are you?)."""

    pass


class AuthorizationError(Exception):
    """Base for all authorization-related errors (what can you do?)."""

    pass


class ApplicationError(Exception):
    """Base for all application service-level errors."""

    pass


# =============================================================================
# Validation Errors (Input/Format validation)
# =============================================================================


class InvalidEmail(ValidationError):
    def __init__(self, email: str):
        super().__init__(f"Invalid email: {email}")
        self.email = email


class InvalidUsername(ValidationError):
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


class InvalidPassword(ValidationError):
    def __init__(self, password: str, min_length: int = 8):
        super().__init__(
            f"Invalid password: {password}. Passwords must be at least {min_length} characters long."
        )
        self.password = password


# =============================================================================
# Domain Errors (Business Logic violations)
# =============================================================================


class UsernameTaken(DomainError):
    def __init__(self, username: str):
        super().__init__(f"Username already taken: {username}")
        self.username = username


class EmailTaken(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Email already taken: {email}")
        self.email = email


class UserNotFoundError(DomainError):
    def __init__(self, username_or_email: str):
        super().__init__(f"User not found: {username_or_email}")
        self.username_or_email = username_or_email


# =============================================================================
# Application Service Errors
# =============================================================================


class PasswordsDoNotMatchError(ApplicationError):
    def __init__(self):
        super().__init__("Passwords do not match. Please try again.")


# =============================================================================
# Authentication Errors (Identity verification)
# =============================================================================


class InvalidCredentialsError(AuthenticationError):
    def __init__(
        self,
        message: str = "Authentication failed. Please check your credentials.",
    ):
        super().__init__(message)
        self.message = message


# =============================================================================
# Authorization Errors (Permission verification)
# =============================================================================


class UserNotAuthorizedError(AuthorizationError):
    def __init__(self):
        super().__init__("User not authorized. Please try again.")


# =============================================================================
# Infrastructure Errors
# =============================================================================


class UserCreationError(InfrastructureError):
    def __init__(self):
        super().__init__("Error creating user. Please try again later.")
