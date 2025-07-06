from contextlib import contextmanager

from flask import template_rendered


@contextmanager
def capture_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestAuth:
    def test_protected_redirects_if_not_logged_in(self, client):
        resp = client.get("/protected", follow_redirects=False)
        # Flask-Login default is a 302 redirect to /login
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_login_with_bad_credentials(self, client, app):
        with capture_templates(app) as templates:
            resp = client.post(
                "/login",
                data={"username": "admin", "password": "wrong"},
                follow_redirects=True,
            )

        assert resp.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert "error" in context

    def test_login_logout_flow(self, client):
        # log in
        resp = client.post(
            "/login",
            data={"username": "admin", "password": "test123"},
            follow_redirects=True,
        )
        assert b"Hello admin!" in resp.data

        # now /protected should work
        resp2 = client.get("/protected")
        assert resp2.status_code == 200

        # log out
        resp3 = client.get("/logout", follow_redirects=True)

        # after logout, protected is back to redirect
        resp4 = client.get("/protected", follow_redirects=False)
        assert resp4.status_code == 302
        assert "/login" in resp4.headers["Location"]

    def test_user_creation_fails_on_bad_credentials(self, client):
        resp = client.post(
            "/register",
            data={
                "username": "newuser",
                "email": "newuser@example@.com",
                "password": "test123",
                "password2": "test123",
            },
        )

        repo = client.application.extensions["user_repo"]
        user = repo.find_by_username("newuser")
        assert user is None
