import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ingestion_api.api.dependencies.auth import AdminUser, get_current_user
from ingestion_api.domain.users.enums import UserRole


@pytest.fixture
def app():
    app = FastAPI()

    @app.get("/admin-route")
    async def admin_route(admin: AdminUser):
        return {"message": "Admin access granted"}

    return app


def test_admin_access_granted(app):
    class FakeAdmin:
        role = UserRole.ADMIN

    app.dependency_overrides[get_current_user] = lambda: FakeAdmin()
    response = TestClient(app).get("/admin-route")

    assert response.status_code == 200
    assert response.json() == {"message": "Admin access granted"}


def test_user_is_forbidden(app):
    class FakeUser:
        role = UserRole.USER

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    response = TestClient(app).get("/admin-route")

    assert response.status_code == 403


def test_guest_is_forbidden(app):
    class FakeGuest:
        role = UserRole.GUEST

    app.dependency_overrides[get_current_user] = lambda: FakeGuest()
    response = TestClient(app).get("/admin-route")

    assert response.status_code == 403
