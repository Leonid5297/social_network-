import requests
from http import HTTPStatus

ENDPOINT = "http://10.114.7.146:5000"


def test_create_user():
    payload = {
        "username": "leoEnid3596",
        "email": "test@test.com",
        "password": "London@192j",
    }  # it is a correct json
    # the transmitted payload is correct:
    result = requests.post(f"{ENDPOINT}/users/create", json=payload)
    response = result.json()
    assert result.status_code == HTTPStatus.CREATED
    assert payload["username"] == response["username"]
    assert payload["email"] == response["email"]
    assert "comments_of_other_users" in response
    assert "reactions_of_other_users" in response
    assert "posts" in response
    assert str(response["user_id"]) in requests.get(f"{ENDPOINT}/users/all").json()

    # test - the transferred username is already occupied (created second user)
    result_2 = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert result_2.status_code == HTTPStatus.BAD_REQUEST
    # delete created user:
    payload_deleting_user = {
        "user_id": result.json()["user_id"],
        "password_author": "London@192j",
    }
    delete_user = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user
    )
    assert delete_user.status_code == HTTPStatus.OK

    # test - the transmitted payload with incorrect password:
    payload["password"] = "@@@@@@@@"
    result = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert result.status_code == HTTPStatus.BAD_REQUEST
    payload["password"] = "London@192j"

    # test - the transmitted payload with incorrect username:
    payload["username"] = "000"
    result = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert result.status_code == HTTPStatus.BAD_REQUEST
    payload["username"] = "leoEnid3596"

    # test the transmitted payload with incorrect email:
    payload["email"] = "qwerty"
    result = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert result.status_code == HTTPStatus.BAD_REQUEST
    payload["email"] = "test@test.com"


def test_get_data_user():
    payload_user = {
        "username": "l1eon4id36",
        "email": "test14@test.com",
        "password": "LIon1d4n@j",
    }  # it is a correct json
    # transmitted user_id is incorrect:
    result_get = requests.get(f"{ENDPOINT}/users/{-1}")
    assert result_get.status_code == HTTPStatus.NOT_FOUND

    # transmitted user_id (user) exists:
    result_user = requests.post(
        f"{ENDPOINT}/users/create", json=payload_user
    )  # create user
    result_get = requests.get(f"{ENDPOINT}/users/{result_user.json()['user_id']}")
    response = result_get.json()
    assert result_get.status_code == HTTPStatus.OK
    assert result_user.json()["user_id"] == response["user_id"]
    assert payload_user["username"] == response["username"]
    assert payload_user["email"] == response["email"]
    assert "comments_of_other_users" in response
    assert "reactions_of_other_users" in response
    assert "posts" in response

    # delete created user:
    payload_deleting_user = {
        "user_id": result_user.json()["user_id"],
        "password_author": "LIon1d4n@j",
    }
    delete_user = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user
    )
    assert delete_user.status_code == HTTPStatus.OK


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


def test_delete_user():
    result_user_1 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_1)
    assert result_user_1.status_code == HTTPStatus.CREATED
    result_user_2 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_2)
    assert result_user_2.status_code == HTTPStatus.CREATED
    # create post of user_1
    payload_post = {
        "author_id": result_user_1.json()["user_id"],
        "text": "string",
    }
    result_post = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post
    )  # create post
    assert result_post.status_code == HTTPStatus.CREATED
    payload_review = {
        "author_id": result_user_2.json()["user_id"],  # user_2 - author of the reaction
        "reaction": "like",
        "comment": "cool!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{result_post.json()['post_id']}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED

    # deleting of user:
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
    )  # created post is not in PostArchive
    assert (
            "0" not in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    )  # comment is not in CommentArchive
    assert (
            "0" not in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    )  # reaction is not in ReactionArchive
    assert (
            str(result_user_1.json()["user_id"])
            not in requests.get(f"{ENDPOINT}/users/all").json()
    )  # user is not in UserArchive
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
