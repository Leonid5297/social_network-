import requests
from http import HTTPStatus
import os

ENDPOINT = "http://10.114.7.146:5000"


def test_leaderboard():
    # create user_1 - post_1 - count_reviews = 3 from user_2;
    # create user_2 - post_2 - count_reviews = 2 from user_1;
    payload_user_1 = {
        "username": "iva3n1351",
        "email": "ivan10@test.com",
        "password": "L5on5don@1",
    }

    payload_user_2 = {
        "username": "oleg3531",
        "email": "oleg11@test.com",
        "password": "Lnt32kfa@",
    }
    result_user_1 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_1)
    assert result_user_1.status_code == HTTPStatus.CREATED
    result_user_2 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_2)
    assert result_user_2.status_code == HTTPStatus.CREATED
    payload_post_1 = {
        "author_id": result_user_1.json()["user_id"],
        "text": "string",
    }
    payload_post_2 = {
        "author_id": result_user_2.json()["user_id"],
        "text": "string",
    }
    result_post_1 = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post_1
    )  # create post
    assert result_post_1.status_code == HTTPStatus.CREATED
    post_id_1 = result_post_1.json()["post_id"]
    result_post_2 = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post_2
    )  # create post
    assert result_post_2.status_code == HTTPStatus.CREATED
    post_id_2 = result_post_2.json()["post_id"]
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "like",
        "comment": "it is cool post!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id_1}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id_1}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    payload_review = {
        "author_id": result_user_1.json()["user_id"],
        "reaction": "like",
        "comment": "it is cool post!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id_2}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED

    # test - "type": "list", "sort": "asc"
    payload_leaderboard = {"type": "list", "sort": "asc"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert result_leaderboard.json()["users"][0]["count_reactions"] == 2
    assert result_leaderboard.json()["users"][1]["count_reactions"] == 3
    assert result_leaderboard.json()["users"][0]["username"] == "oleg3531"
    assert result_leaderboard.json()["users"][1]["username"] == "iva3n1351"

    # test - "type": "list", "sort": "desc"
    payload_leaderboard = {"type": "list", "sort": "desc"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert result_leaderboard.json()["users"][0]["count_reactions"] == 3
    assert result_leaderboard.json()["users"][1]["count_reactions"] == 2
    assert result_leaderboard.json()["users"][0]["username"] == "iva3n1351"
    assert result_leaderboard.json()["users"][1]["username"] == "oleg3531"
    # test - "type": "list"
    payload_leaderboard = {"type": "list"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert len(result_leaderboard.json()["users"]) == 2

    # test - "type": "graph", "sort": "asc"
    payload_leaderboard = {"type": "graph", "sort": "asc"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert result_leaderboard.text == "<img src='/static/users_leaderboard.png'>"
    # test - "type": "graph", "sort": "desc"
    payload_leaderboard = {"type": "graph", "sort": "desc"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert result_leaderboard.text == "<img src='/static/users_leaderboard.png'>"
    # test - "type": "graph"
    payload_leaderboard = {
        "type": "graph",
    }
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.OK
    assert result_leaderboard.text == "<img src='/static/users_leaderboard.png'>"

    # test - BAD_REQUESTS
    payload_leaderboard = {"type": "graph999"}
    result_leaderboard = requests.get(
        f"{ENDPOINT}/users/leaderboard", json=payload_leaderboard
    )
    assert result_leaderboard.status_code == HTTPStatus.BAD_REQUEST

    # deleting everything
    payload_deleting_user_1 = {
        "user_id": result_user_1.json()["user_id"],
        "password_author": "L5on5don@1",
    }
    delete_user_1 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_1
    )
    assert delete_user_1.status_code == HTTPStatus.OK

    payload_deleting_user_2 = {
        "user_id": result_user_2.json()["user_id"],
        "password_author": "Lnt32kfa@",
    }
    delete_user_2 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_2
    )
    assert delete_user_2.status_code == HTTPStatus.OK
    os.remove("C:/flask_project/app/static/users_leaderboard.png")
