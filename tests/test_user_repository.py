from src.core.errors import InvalidEmail, InvalidUsername, UsernameTaken
from src.core.user import User
from src.infra.repositories.in_memory_user import InMemoryUserRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository

# SQL Repository Tests


def test_register_and_find_sql_valid_user(db, bcrypt):
    """Test successful user registration and retrieval with SQL repository."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert isinstance(user, User)

    fetched = repo.find_by_username("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None


def test_register_sql_invalid_email(db, bcrypt):
    """Test user registration fails with invalid email format."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "invalid-email", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidEmail)
    assert error.email == "invalid-email"


def test_register_sql_invalid_username_too_short(db, bcrypt):
    """Test user registration fails with username that is too short."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("ab", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)
    assert error.username == "ab"


def test_register_sql_invalid_username_special_chars(db, bcrypt):
    """Test user registration fails with username containing invalid characters."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob@invalid", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)
    assert error.username == "bob@invalid"


def test_register_sql_duplicate_username(db, bcrypt):
    """Test user registration fails when username is already taken."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    # Register first user
    result1 = repo.register("bob", "bob@example.com", "hunter2")
    assert result1.is_ok

    # Try to register with same username
    result2 = repo.register("bob", "different@example.com", "password")
    assert result2.is_err
    error = result2.unwrap_err()
    assert isinstance(error, UsernameTaken)
    assert error.username == "bob"


def test_register_sql_duplicate_email(db, bcrypt):
    """Test user registration fails when email is already taken."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    # Register first user
    result1 = repo.register("bob", "bob@example.com", "hunter2")
    assert result1.is_ok

    # Try to register with same email
    result2 = repo.register("alice", "bob@example.com", "password")
    assert result2.is_err
    error = result2.unwrap_err()
    assert isinstance(error, UsernameTaken)


def test_find_by_username_or_email_sql(db, bcrypt):
    """Test finding user by username or email with SQL repository."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok

    fetched = repo.find_by_username_or_email("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None

    fetched_by_email = repo.find_by_username_or_email("bob@example.com")
    assert fetched_by_email and fetched_by_email.username == "bob"
    assert fetched_by_email.pw_hash is None


def test_load_for_auth_sql(db, bcrypt):
    """Test loading user with password hash for authentication with SQL repository."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok

    fetched = repo.load_for_auth("bob")
    assert fetched and fetched.username == "bob"
    assert fetched.email == "bob@example.com"
    assert repo.verify_password(fetched, "hunter2")


def test_first_user_is_admin_sql(db, bcrypt):
    """Test that the first registered user becomes admin with SQL repository."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    users = repo.list_all()
    for user in users:
        repo.delete(user.username)

    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert user.is_admin


def test_register_sql_valid_username_with_underscores_and_hyphens(db, bcrypt):
    """Test user registration succeeds with valid username containing underscores and hyphens."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob_alice-123", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert user.username == "bob_alice-123"


# In-Memory Repository Tests


def test_register_and_find_in_memory_valid_user(db, bcrypt):
    """Test successful user registration and retrieval with in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert isinstance(user, User)

    fetched = repo.find_by_username("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None


def test_register_in_memory_invalid_email(db, bcrypt):
    """Test user registration fails with invalid email format in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "invalid-email", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidEmail)
    assert error.email == "invalid-email"


def test_register_in_memory_invalid_username_too_short(db, bcrypt):
    """Test user registration fails with username that is too short in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("ab", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)
    assert error.username == "ab"


def test_register_in_memory_invalid_username_special_chars(db, bcrypt):
    """Test user registration fails with username containing invalid characters in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob@invalid", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)
    assert error.username == "bob@invalid"


def test_register_in_memory_duplicate_username(db, bcrypt):
    """Test user registration fails when username is already taken in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    # Register first user
    result1 = repo.register("bob", "bob@example.com", "hunter2")
    assert result1.is_ok

    # Try to register with same username
    result2 = repo.register("bob", "different@example.com", "password")
    assert result2.is_err
    error = result2.unwrap_err()
    assert isinstance(error, UsernameTaken)
    assert error.username == "bob"


def test_find_by_username_or_email_in_memory(db, bcrypt):
    """Test finding user by username or email with in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok

    fetched = repo.find_by_username_or_email("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None

    fetched_by_email = repo.find_by_username_or_email("bob@example.com")
    assert fetched_by_email and fetched_by_email.username == "bob"
    assert fetched_by_email.pw_hash is None


def test_load_for_auth_in_memory(db, bcrypt):
    """Test loading user with password hash for authentication with in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok

    fetched = repo.load_for_auth("bob")
    assert fetched and fetched.username == "bob"
    assert fetched.email == "bob@example.com"
    assert repo.verify_password(fetched, "hunter2")


def test_first_user_is_admin_in_memory(db, bcrypt):
    """Test that the first registered user becomes admin with in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert user.is_admin


def test_register_in_memory_valid_username_with_underscores_and_hyphens(
    db, bcrypt
):
    """Test user registration succeeds with valid username containing underscores and hyphens in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob_alice-123", "bob@example.com", "hunter2")
    assert result.is_ok
    user = result.unwrap()
    assert user.username == "bob_alice-123"


# Edge Cases


def test_register_sql_empty_username(db, bcrypt):
    """Test user registration fails with empty username."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)


def test_register_sql_empty_email(db, bcrypt):
    """Test user registration fails with empty email."""
    repo = SQLUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidEmail)


def test_register_in_memory_empty_username(db, bcrypt):
    """Test user registration fails with empty username in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("", "bob@example.com", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidUsername)


def test_register_in_memory_empty_email(db, bcrypt):
    """Test user registration fails with empty email in in-memory repository."""
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    result = repo.register("bob", "", "hunter2")
    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, InvalidEmail)
