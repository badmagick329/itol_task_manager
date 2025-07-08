from abc import ABC, abstractmethod
from typing import Union

from src.core.errors import DomainError, InfrastructureError, ValidationError
from src.core.result import Result
from src.core.task import Task

RepositoryError = Union[DomainError, ValidationError, InfrastructureError]


class TaskRepository(ABC):
    max_title_length = 100
    max_description_length = 500

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None: ...

    @abstractmethod
    def list_all(self) -> list[Task]: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Task]: ...

    @abstractmethod
    def create(
        self,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> Result[Task, RepositoryError]: ...

    @abstractmethod
    def update(
        self,
        task_id: int,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> Result[Task, RepositoryError]: ...

    @abstractmethod
    def delete(self, task_id: int) -> None | DomainError: ...
