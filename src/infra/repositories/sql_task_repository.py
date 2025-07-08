from sqlite3 import Connection, IntegrityError

from src.core.errors import (
    DomainError,
    InfrastructureError,
    TaskNotFoundError,
    ValidationError,
)
from src.core.ports.task_repository import RepositoryError, TaskRepository
from src.core.result import Result
from src.core.task import Task
from src.infra.db import get_connection


class SQLTaskRepository(TaskRepository):
    def get_by_id(self, task_id: int) -> Task | None:
        """Retrieves a task by its ID.

        Args:
            task_id (int): The ID of the task to retrieve.
        Returns:
            Task | None: The task with the specified ID, or None if not found.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, user_id, title, description, due_date, status FROM tasks WHERE id = ?",
            (task_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        task = Task(
            id=task_id,
            title=row["title"],
            description=row["description"],
            due_date=row["due_date"],
            status=row["status"],
            user_id=row["user_id"],
        )
        return task

    def list_all(self) -> list[Task]:
        """Lists all tasks in the repository. WARNING: This method retrieves all tasks without filtering by user.

        Returns:
            list[Task]: A list of all tasks.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, user_id, title, description, due_date, status FROM tasks"
        )
        tasks: list[Task] = []
        for row in cur.fetchall():
            task = Task(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                due_date=row["due_date"],
                status=row["status"],
                user_id=row["user_id"],
            )
            tasks.append(task)
        return tasks

    def list_by_user(self, user_id: int) -> list[Task]:
        """Lists all tasks for a specific user.

        Args:
            user_id (int): The ID of the user whose tasks to retrieve.

        Returns:
            list[Task]: A list of tasks for the specified user.
        """
        conn = self._get_connection()
        cur = conn.execute(
            "SELECT id, user_id, title, description, due_date, status FROM tasks WHERE user_id = ?",
            (user_id,),
        )
        tasks: list[Task] = []
        for row in cur.fetchall():
            task = Task(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                due_date=row["due_date"],
                status=row["status"],
                user_id=row["user_id"],
            )
            tasks.append(task)
        return tasks

    def create(
        self,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> Result[Task, RepositoryError]:
        """Creates a new task in the repository.

        Args:
            title (str): The title of the task.
            description (str): The description of the task.
            due_date (str): The due date of the task.
            status (str): The status of the task.
            user_id (int): The ID of the user who owns the task.

        Returns:
            Result[Task, RepositoryError]: The created task or an error if creation failed."""
        created_task_result = Task.create(
            id=0,  # ID will be assigned by the database
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            user_id=user_id,
        )
        if created_task_result.is_err:
            return Result.Err(created_task_result.unwrap_err())
        task = created_task_result.unwrap()

        conn = self._get_connection()
        try:
            cur = conn.execute(
                "INSERT INTO tasks (user_id, title, description, due_date, status) VALUES (?, ?, ?, ?, ?)",
                (
                    task.user_id,
                    task.title,
                    task.description,
                    task.due_date,
                    task.status,
                ),
            )
            conn.commit()
            task_id = cur.lastrowid
            if task_id is None:
                return Result.Err(
                    InfrastructureError("Failed to retrieve created task id")
                )
            new_task = self.get_by_id(task_id)
            if not new_task:
                return Result.Err(
                    InfrastructureError("Failed to retrieve created task")
                )
            return Result.Ok(new_task)
        except IntegrityError as e:
            return Result.Err(InfrastructureError(str(e)))

    def update(
        self,
        task_id: int,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> Result[Task, RepositoryError]:
        """Updates an existing task in the repository.

        Args:
            task_id (int): The ID of the task to update.
            title (str): The new title of the task.
            description (str): The new description of the task.
            due_date (str): The new due date of the task.
            status (str): The new status of the task.
            user_id (int): The ID of the user who owns the task.

        Returns:
            Result[Task, RepositoryError]: The updated task or an error if the update failed.
        """

        created_task_result = Task.create(
            id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            user_id=user_id,
        )
        if created_task_result.is_err:
            return Result.Err(created_task_result.unwrap_err())

        task = created_task_result.unwrap()

        conn = self._get_connection()
        try:
            cur = conn.execute(
                "UPDATE tasks SET title = ?, description = ?, due_date = ?, status = ? WHERE id = ?",
                (
                    task.title,
                    task.description,
                    task.due_date,
                    task.status,
                    task.id,
                ),
            )
            conn.commit()
            if cur.rowcount == 0:
                return Result.Err(TaskNotFoundError(task.id))
            updated_task = self.get_by_id(task.id)
            if not updated_task:
                return Result.Err(
                    InfrastructureError("Failed to retrieve updated task")
                )
            return Result.Ok(updated_task)
        except IntegrityError as e:
            return Result.Err(InfrastructureError(str(e)))

    def delete(self, task_id: int) -> None | TaskNotFoundError:
        """Deletes a task by its ID.

        Args:
            task_id (int): The ID of the task to delete.

        Returns:
            None | DomainError: None if deletion was successful, DomainError if task was not found.
        """
        conn = self._get_connection()
        if not self.get_by_id(task_id):
            return TaskNotFoundError(task_id)
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
        conn.commit()

    def _get_connection(self) -> Connection:
        return get_connection()
