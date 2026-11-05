from uuid import uuid4


def _create(client, name="Test User", age=30):
    email = f"test-{uuid4()}@example.com"
    response = client.post("/members", json={"name": name, "email": email, "age": age})
    assert response.status_code == 201
    return response.json()


# ---------- Read ----------
def test_get_members_returns_200(client):
    response = client.get("/members")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_member_returns_200(client):
    created = _create(client)
    response = client.get(f"/members/{created['member_id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_member_returns_404(client):
    response = client.get("/members/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


def test_member_id_validation_returns_422(client):
    response = client.get("/members/not-a-number")
    assert response.status_code == 422


# ---------- Create ----------
def test_create_member_returns_201(client):
    email = f"test-{uuid4()}@example.com"
    response = client.post(
        "/members", json={"name": "Test User", "email": email, "age": 30}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test User"
    assert body["email"] == email
    assert isinstance(body["member_id"], int)


def test_duplicate_email_returns_409(client):
    email = f"duplicate-{uuid4()}@example.com"
    first = client.post("/members", json={"name": "First", "email": email, "age": 30})
    assert first.status_code == 201
    second = client.post("/members", json={"name": "Second", "email": email, "age": 31})
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already exists"


def test_create_member_invalid_email_returns_422(client):
    response = client.post(
        "/members", json={"name": "Bad", "email": "not-an-email", "age": 30}
    )
    assert response.status_code == 422


# ---------- Update ----------
def test_put_member_returns_200(client):
    created = _create(client)
    response = client.put(
        f"/members/{created['member_id']}",
        json={"name": "Updated", "email": created["email"], "age": 41},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["age"] == 41


def test_put_unknown_member_returns_404(client):
    response = client.put(
        "/members/999999",
        json={"name": "X", "email": f"x-{uuid4()}@example.com", "age": 1},
    )
    assert response.status_code == 404


def test_patch_only_changes_given_field(client):
    created = _create(client, name="Keep Name", age=30)
    response = client.patch(f"/members/{created['member_id']}", json={"age": 31})
    assert response.status_code == 200
    body = response.json()
    assert body["age"] == 31
    assert body["name"] == "Keep Name"
    assert body["email"] == created["email"]


def test_patch_empty_body_returns_400(client):
    created = _create(client)
    response = client.patch(f"/members/{created['member_id']}", json={})
    assert response.status_code == 400


def test_patch_explicit_null_returns_422(client):
    created = _create(client)
    response = client.patch(f"/members/{created['member_id']}", json={"email": None})
    assert response.status_code == 422


def test_patch_unknown_member_returns_404(client):
    response = client.patch("/members/999999", json={"age": 1})
    assert response.status_code == 404


# ---------- Delete ----------
def test_delete_member_returns_204(client):
    created = _create(client)
    response = client.delete(f"/members/{created['member_id']}")
    assert response.status_code == 204
    assert client.get(f"/members/{created['member_id']}").status_code == 404


def test_delete_unknown_member_returns_404(client):
    response = client.delete("/members/999999")
    assert response.status_code == 404
