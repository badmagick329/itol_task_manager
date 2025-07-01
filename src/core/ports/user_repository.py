from abc import ABC, abstractmethod

from src.core.user import User


class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def verify_password(self, user: User, password: str) -> bool: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def add(self, user: User) -> None: ...

    @abstractmethod
    def list_all(self) -> list[User]: ...
