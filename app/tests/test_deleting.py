import os
from http import HTTPStatus
import requests

ENDPOINT = "http://10.114.7.146:5000"

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


def test_delete_reaction_comment_post_user():
    result_user_1 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_1)

    result_user_2 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_2)
    # create post of user_1
    payload_post = {
        "author_id": result_user_1.json()["user_id"],
        "text": "string",
    }
    result_post = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post
    )  # create post

    # reaction and comment of user_2 on post of user_1
    payload_review = {
        "author_id": result_user_2.json()["user_id"],  # user_2 - author of the reaction
        "reaction": "like",
        "comment": "cool!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{result_post.json()['post_id']}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    assert "0" in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    assert "0" in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    payload_deleting_reaction = {"password_author": "Lnt32kfa@", "reaction_id": 0}
    payload_deleting_comment = {"password_author": "Lnt32kfa@", "comment_id": 0}
    result_deleting_reaction = requests.delete(
        f"{ENDPOINT}/users/delete/reaction", json=payload_deleting_reaction
    )
    result_deleting_comment = requests.delete(
        f"{ENDPOINT}/users/delete/comment", json=payload_deleting_comment
    )
    assert result_deleting_comment.status_code == HTTPStatus.OK
    assert result_deleting_reaction.status_code == HTTPStatus.OK
    assert "0" not in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    assert "0" not in requests.get(f"{ENDPOINT}/posts/reactions/all").json()

    # Test - deleting of post:
    result_review = requests.post(
        f"{ENDPOINT}/posts/{result_post.json()['post_id']}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    payload_deleting_post = {
        "password_author": "L5on5don@1",
        "post_id": result_post.json()["post_id"],
        "author_id": result_user_1.json()["user_id"],
    }
    result_deleting_post = requests.delete(
        f"{ENDPOINT}/users/delete/post", json=payload_deleting_post
    )
    assert result_deleting_post.status_code == HTTPStatus.OK
    assert (
        str(result_post.json()["post_id"])
        not in requests.get(f"{ENDPOINT}/posts/all").json()
    )
    assert (
        "0" not in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    )  # reaction_id
    assert (
        "0" not in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    )  # comment_id

    # Test - deleting of user:
    result_post = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post
    )  # create post
    result_review = requests.post(
        f"{ENDPOINT}/posts/{result_post.json()['post_id']}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    payload_deleting_user = {
        "user_id": result_user_1.json()["user_id"],
        "password_author": "L5on5don@1",
    }
    result_deleting_user = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user
    )
    assert result_deleting_user.status_code == HTTPStatus.OK
    assert (
        result_post.json()["post_id"]
        not in requests.get(f"{ENDPOINT}/posts/all").json()
    )
    assert (
        "0" not in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    )  # reaction_id
    assert (
        "0" not in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    )  # comment_id
    assert (
        str(result_user_1.json()["user_id"])
        not in requests.get(f"{ENDPOINT}/users/all").json()
    )
    # deleting of user_2
    payload_deleting_user_2 = {
        "user_id": result_user_2.json()["user_id"],
        "password_author": "Lnt32kfa@",
    }
    delete_user_2 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_2
    )
    assert delete_user_2.status_code == HTTPStatus.OK
    assert (
        str(result_user_2.json()["user_id"])
        not in requests.get(f"{ENDPOINT}/users/all").json()
    )
