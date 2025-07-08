import csv
import io

from src.core.errors import InfrastructureError
from src.core.ports.task_repository import TaskRepository
from src.core.result import Result


class TaskExportService:
    """
    Service responsible for exporting tasks in CSV format.
    """

    def __init__(self, task_repo: TaskRepository) -> None:
        """
        Initialize TaskExportService with a task repository.

        Args:
            task_repo (TaskRepository): Repository for task data operations.
        """
        self.task_repo = task_repo

    def export_user_tasks(
        self, user_id: int
    ) -> Result[str, InfrastructureError]:
        """
        Generate CSV content for a specified user's tasks and return as a string.

        Args:
            user_id (int): The ID of the user whose tasks to export.

        Returns:
            Result[str, InfrastructureError]: Ok with the CSV content on success, Err with InfrastructureError on failure.
        """
        tasks = self.task_repo.list_by_user(user_id)
        try:
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(
                ["id", "title", "description", "due_date", "status"]
            )
            for task in tasks:
                writer.writerow(
                    [
                        task.id,
                        task.title,
                        task.description,
                        task.due_date,
                        task.status,
                    ]
                )
            csv_content = buffer.getvalue()
            buffer.close()
            return Result.Ok(csv_content)
        except Exception as e:
            return Result.Err(InfrastructureError(str(e)))
