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
