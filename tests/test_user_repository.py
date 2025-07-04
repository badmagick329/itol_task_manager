from src.core.user import User
from src.infra.repositories.in_memory_user import InMemoryUserRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository


def test_register_and_find(db, bcrypt):
    repo = SQLUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")
    assert isinstance(user, User)
    fetched = repo.find_by_username("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None


def test_find_by_username_or_email(db, bcrypt):
    repo = SQLUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")
    assert isinstance(user, User)
    fetched = repo.find_by_username_or_email("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None

    fetched_by_email = repo.find_by_username_or_email("bob@example.com")
    assert fetched_by_email and fetched_by_email.username == "bob"
    assert fetched_by_email.pw_hash is None


def test_load_for_auth(db, bcrypt):
    repo = SQLUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")

    assert isinstance(user, User)
    fetched = repo.load_for_auth("bob")
    assert fetched and fetched.username == "bob"
    assert fetched.email == "bob@example.com"
    assert repo.verify_password(fetched, "hunter2")


def test_register_and_find_in_memory(db, bcrypt):
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")
    assert isinstance(user, User)
    fetched = repo.find_by_username("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None


def test_find_by_username_or_email_in_memory(db, bcrypt):
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")
    assert isinstance(user, User)
    fetched = repo.find_by_username_or_email("bob")
    assert fetched and fetched.email == "bob@example.com"
    assert fetched.pw_hash is None

    fetched_by_email = repo.find_by_username_or_email("bob@example.com")
    assert fetched_by_email and fetched_by_email.username == "bob"
    assert fetched_by_email.pw_hash is None


def test_load_for_auth_in_memory(db, bcrypt):
    repo = InMemoryUserRepository(bcrypt=bcrypt)
    user = repo.register("bob", "bob@example.com", "hunter2")

    assert isinstance(user, User)
    fetched = repo.load_for_auth("bob")
    assert fetched and fetched.username == "bob"
    assert fetched.email == "bob@example.com"
    assert repo.verify_password(fetched, "hunter2")
