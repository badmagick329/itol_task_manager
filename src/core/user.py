from abc import ABC, abstractmethod


class User:
    def __init__(self, id: int, username: str, pw_hash: str):
        self.id = id
        self.username = username
        self.pw_hash = pw_hash


class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def verify_password(self, user: User, password: str) -> bool: ...
