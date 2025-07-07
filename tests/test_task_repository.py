from datetime import date

from src.core.errors import InfrastructureError, ValidationError
from src.core.task import Task
from src.infra.repositories.sql_task_repository import SQLTaskRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository


# SQL Task Repository Tests
def test_create_and_get_task(db, bcrypt, test_admin):
    """Test creating a valid task."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None

    repo = SQLTaskRepository()

    task = Task(
        id=0,
        title="Test Task",
        description="A description",
        due_date=str(date.today()),
        status="To Do",
        user_id=int(user.id),
    )
    result = repo.create(task)
    assert result.is_ok, f"Error creating task: {result.unwrap_err()}"
    created = result.unwrap()
    assert isinstance(created, Task)
    assert created.id != 0
    assert created.title == "Test Task"
    assert created.description == "A description"
    assert created.status == "To Do"


def test_list_all_and_list_by_user(db, bcrypt, test_admin):
    """Test listing tasks for user and all tasks."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    # Ensure repo is empty? In case test tasks are added as fixture at some point
    conn = db
    conn.execute("DELETE FROM tasks;")
    conn.commit()

    t1 = repo.create(
        Task(0, "T1", "", str(date.today()), "To Do", user.id)
    ).unwrap()
    t2 = repo.create(
        Task(0, "T2", "", str(date.today()), "In Progress", user.id)
    ).unwrap()

    all_tasks = repo.list_all()
    assert any(t.id == t1.id for t in all_tasks)
    assert any(t.id == t2.id for t in all_tasks)

    user_tasks = repo.list_by_user(user.id)
    assert all(t.user_id == user.id for t in user_tasks)
    ids = {t.id for t in user_tasks}
    assert t1.id in ids and t2.id in ids


def test_update_task(db, bcrypt, test_admin):
    """Test updating an existing task."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    # create task
    t = repo.create(
        Task(0, "Old", "Desc", str(date.today()), "To Do", user.id)
    ).unwrap()
    # update fields
    t.title = "Updated"
    t.status = "Completed"
    result = repo.update(t)
    assert result.is_ok, f"Error updating: {result.unwrap_err()}"
    updated = result.unwrap()
    assert updated.title == "Updated"
    assert updated.status == "Completed"


def test_delete_task(db, bcrypt, test_admin):
    """Test deleting a task."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    t = repo.create(
        Task(0, "Tmp", "", str(date.today()), "To Do", user.id)
    ).unwrap()

    err = repo.delete(t.id)
    assert err is None
    assert repo.get_by_id(t.id) is None


def test_create_task_invalid_status(db, bcrypt, test_admin):
    """Invalid status should raise InfrastructureError due to SQL CHECK."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    bad = Task(0, "Bad", "", str(date.today()), "Not a Status", user.id)
    result = repo.create(bad)
    assert result.is_err
    assert isinstance(result.unwrap_err(), InfrastructureError)


def test_create_task_title_length(db, bcrypt, test_admin):
    """Title longer than 100 chars should error."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    long_title = "x" * 101
    bad = Task(0, long_title, "", str(date.today()), "To Do", user.id)
    result = repo.create(bad)
    assert result.is_err
    assert isinstance(result.unwrap_err(), InfrastructureError)


def test_create_task_description_length(db, bcrypt, test_admin):
    """Description longer than 500 chars should error."""
    user_repo = SQLUserRepository(bcrypt=bcrypt)
    user = user_repo.find_by_username(test_admin["username"])
    assert user is not None
    repo = SQLTaskRepository()

    long_desc = "x" * 501
    bad = Task(0, "DescTest", long_desc, str(date.today()), "To Do", user.id)
    result = repo.create(bad)
    assert result.is_err
    assert isinstance(result.unwrap_err(), InfrastructureError)


# Domain-level validation tests for Task.create
def test_task_create_empty_title():
    """Task.create should fail when title is empty."""
    result = Task.create(
        id=1,
        title="",
        description="Some description",
        due_date=str(date.today()),
        status="To Do",
        user_id=1,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "Title is required" in str(err)


def test_task_create_long_title():
    """Task.create should fail when title exceeds max length."""
    long_title = "x" * 101
    result = Task.create(
        id=1,
        title=long_title,
        description="desc",
        due_date=str(date.today()),
        status="To Do",
        user_id=1,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "100 characters" in str(err)


def test_task_create_long_description():
    """Task.create should fail when description exceeds max length."""
    long_desc = "x" * 501
    result = Task.create(
        id=1,
        title="Title",
        description=long_desc,
        due_date=str(date.today()),
        status="To Do",
        user_id=1,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "500 characters" in str(err)


def test_task_create_invalid_date():
    """Task.create should fail when due_date is invalid."""
    result = Task.create(
        id=1,
        title="Title",
        description="desc",
        due_date="invalid-date",
        status="To Do",
        user_id=1,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "valid date" in str(err)


def test_task_create_invalid_status():
    """Task.create should fail when status is not an allowed option."""
    result = Task.create(
        id=1,
        title="Title",
        description="desc",
        due_date=str(date.today()),
        status="Unknown",
        user_id=1,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "Status must be one of" in str(err)


def test_task_create_invalid_user_id():
    """Task.create should fail when user_id is non-positive."""
    result = Task.create(
        id=1,
        title="Title",
        description="desc",
        due_date=str(date.today()),
        status="To Do",
        user_id=0,
    )
    assert result.is_err
    err = result.unwrap_err()
    assert isinstance(err, ValidationError)
    assert "User ID must be a positive integer" in str(err)


def test_task_create_valid():
    """Task.create should succeed for valid inputs."""
    result = Task.create(
        id=1,
        title="Title",
        description="desc",
        due_date=str(date.today()),
        status="In Progress",
        user_id=1,
    )
    assert result.is_ok
    task = result.unwrap()
    assert isinstance(task, Task)
    assert task.title == "Title"
    assert task.status == "In Progress"
    assert task.user_id == 1
