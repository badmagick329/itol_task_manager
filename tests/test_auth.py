class TestAuth:
    def test_protected_redirects_if_not_logged_in(self, client):
        resp = client.get("/protected", follow_redirects=False)
        # Flask-Login default is a 302 redirect to /login
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_login_with_bad_credentials(self, client):
        resp = client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
        )
        assert resp.status_code == 401

    def test_login_logout_flow(self, client):
        # log in
        resp = client.post(
            "/login",
            data={"username": "admin", "password": "test123"},
            follow_redirects=True,
        )
        assert b"Hello, admin!" in resp.data

        # now /protected should work
        resp2 = client.get("/protected")
        assert resp2.status_code == 200
        assert b"protected page" in resp2.data

        # log out
        resp3 = client.get("/logout", follow_redirects=True)
        assert b"Logged out" in resp3.data

        # after logout, protected is back to redirect
        resp4 = client.get("/protected", follow_redirects=False)
        assert resp4.status_code == 302
        assert "/login" in resp4.headers["Location"]
