def test_dashboard_redirects_if_not_logged_in(client):
    """Test that accessing the /dashboard route redirects to login if not logged in."""
    resp = client.get("/dashboard", follow_redirects=False)
    # Flask-Login default is a 302 redirect to /login
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_login_with_bad_credentials(client, app):
    """Test that login fails with incorrect credentials."""
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=False,
    )
    # JSON responses always return HTTP 200; error code is in response body
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is False
    assert data.get("status") == 401
    assert "error" in data


def test_login_logout_flow(client):
    """Test the login and logout flow."""
    # log in
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "test123"},
        follow_redirects=False,
    )
    data = resp.get_json()
    assert data["ok"] is True
    assert data.get("status") == 200
    # Ensure redirect path provided
    assert data.get("redirect") == "/dashboard"

    # now /dashboard should work
    resp2 = client.get(data.get("redirect"), follow_redirects=True)
    assert resp2.status_code == 200

    # log out
    resp3 = client.get("/logout", follow_redirects=True)

    # after logout, /dashboard is back to redirect
    resp4 = client.get("/dashboard", follow_redirects=False)
    assert resp4.status_code == 302
    assert "/login" in resp4.headers["Location"]


def test_user_creation_fails_on_bad_credentials(client):
    """Test that user registration fails with invalid email format."""
    resp = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@example@.com",
            "password": "test123",
            "password2": "test123",
        },
        follow_redirects=False,
    )
    # JSON responses always return HTTP 200; error code is in response body
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is False
    assert data.get("status") == 400
    assert "error" in data

    repo = client.application.extensions["user_repo"]
    user = repo.find_by_username("newuser")
    assert user is None
