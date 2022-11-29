import pytest


@pytest.mark.order(1)
def test_post_create_user1(api_client_user1):
    """Create 2 posts with user 1"""
    for n in (1, 2):
        response = api_client_user1.post(
            "/post/",
            json={
                "text": f"hello test {n}",
            },
        )
        assert response.status_code == 201
        result = response.json()
        assert result["text"] == f"hello test {n}"
        assert result["parent_id"] is None


@pytest.mark.order(2)
def test_reply_on_post_1(api_client, api_client_user1, api_client_user2):
    """each user will add a reply to the first post"""
    posts = api_client.get("/post/user/user1/").json()
    first_post = posts[0]
    for n, client in enumerate((api_client_user1, api_client_user2), 1):
        response = client.post(
            "/post/",
            json={
                "text": f"reply from user{n}",
                "parent_id": first_post["id"],
            },
        )
        assert response.status_code == 201
        result = response.json()
        assert result["text"] == f"reply from user{n}"
        assert result["parent_id"] == first_post["id"]


@pytest.mark.order(3)
def test_post_list_without_replies(api_client):
    response = api_client.get("/post/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    for result in results:
        assert result["parent_id"] is None
        assert "hello test" in result["text"]


@pytest.mark.order(3)
def test_post1_detail(api_client):
    posts = api_client.get("/post/user/user1/").json()
    first_post = posts[0]
    first_post_id = first_post["id"]

    response = api_client.get(f"/post/{first_post_id}/")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == first_post_id
    assert result["user_id"] == first_post["user_id"]
    assert result["text"] == "hello test 1"
    assert result["parent_id"] is None
    replies = result["replies"]
    assert len(replies) == 2
    for reply in replies:
        assert reply["parent_id"] == first_post_id
        assert "reply from user" in reply["text"]


@pytest.mark.order(3)
def test_all_posts_from_user1(api_client):
    response = api_client.get("/post/user/user1/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    for result in results:
        assert result["parent_id"] is None
        assert "hello test" in result["text"]


@pytest.mark.order(3)
def test_all_posts_from_user1_with_replies(api_client):
    response = api_client.get(
        "/post/user/user1/", params={"include_replies": True}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
