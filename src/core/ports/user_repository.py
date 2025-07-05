from abc import ABC, abstractmethod

from src.core.errors import DomainError
from src.core.result import Result
from src.core.user import User


class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def find_by_username_or_email(
        self, username_or_email: str
    ) -> User | None: ...

    @abstractmethod
    def load_for_auth(self, username_or_email: str) -> User | None: ...

    @abstractmethod
    def verify_password(self, user: User, password: str) -> bool: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def list_all(self) -> list[User]: ...

    @abstractmethod
    def register(
        self, username: str, email: str, password: str
    ) -> Result[User, DomainError]: ...

    @abstractmethod
    def delete(self, username_or_email: str) -> None | DomainError: ...
