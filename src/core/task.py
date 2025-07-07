from datetime import date

from src.core.errors import ValidationError
from src.core.result import Result


class Task:
    id: int
    title: str
    description: str
    due_date: str
    status: str
    user_id: int

    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> None:
        """Initializes a Task instance. Does not validate the parameters.

        Args:
            id (int): Unique identifier for the task.
            title (str): The title of the task.
            description (str): The description of the task.
            due_date (str): The due date of the task.
            status (str): The status of the task.
            user_id (int): The ID of the user who created the task.
        """
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.user_id = user_id

    @classmethod
    def create(
        cls,
        id: int,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> Result["Task", ValidationError]:
        """Creates a new Task instance. Use this method instead of the constructor to ensure validation.

        Args:
            id (int): Unique identifier for the task.
            title (str): The title of the task.
            description (str): The description of the task.
            due_date (str): The due date of the task.
            status (str): The status of the task.
            user_id (int): The ID of the user who created the task.

        Returns:
            Result["Task", ValidationError]: The created Task instance or a ValidationError.
        """
        err = cls._validate(
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            user_id=user_id,
        )
        if err is not None:
            return Result.Err(err)

        return Result.Ok(
            cls(
                id=id,
                title=title,
                description=description,
                due_date=due_date,
                status=status,
                user_id=user_id,
            )
        )

    @classmethod
    def _validate(
        cls,
        title: str,
        description: str,
        due_date: str,
        status: str,
        user_id: int,
    ) -> ValidationError | None:
        """Validates the parameters for creating a Task instance.

        Args:
            title (str): The title of the task.
            description (str): The description of the task.
            due_date (str): The due date of the task.
            status (str): The status of the task.
            user_id (int): The ID of the user who created the task.

        Returns:
            ValidationError | None: A ValidationError if validation fails, None otherwise.
        """
        if not title or len(title) > 100:
            return ValidationError(
                "Title is required and must be 100 characters or less."
            )

        if len(description) > 500:
            return ValidationError(
                "Description must be 500 characters or less."
            )

        if not cls._is_valid_date(due_date):
            return ValidationError("Due date must be a valid date.")

        if status not in ["To Do", "In Progress", "Completed"]:
            return ValidationError(
                "Status must be one of: 'To Do', 'In Progress', 'Completed'."
            )

        if user_id <= 0:
            return ValidationError("User ID must be a positive integer.")

        return None

    @staticmethod
    def _is_valid_date(date_string: str) -> bool:
        """Checks if the provided date string is a valid ISO format date.

        Args:
            date_string (str): The date string to validate.

        Returns:
            bool: True if the date string is a valid ISO format date, False otherwise.
        """
        try:
            date.fromisoformat(date_string)
            return True
        except ValueError:
            return False
