import requests
from http import HTTPStatus

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


def test_create_post():
    result_user = requests.post(
        f"{ENDPOINT}/users/create", json=payload_user_1
    )  # create user
    payload_post = {
        "author_id": result_user.json()["user_id"],
        "text": "string",
    }
    # the transmitted payload is correct:
    result = requests.post(f"{ENDPOINT}/posts/create", json=payload_post)  # create post
    response = result.json()
    assert result.status_code == HTTPStatus.CREATED
    assert payload_post["author_id"] == response["author_id"]
    assert payload_post["text"] == response["text"]
    assert "post_id" in response
    assert "author_post_name" in response
    assert "reactions" in response
    assert "comments" in response
    assert (
        str(response["post_id"]) in requests.get(f"{ENDPOINT}/posts/all").json()
    )  # presence in the archive

    # the transmitted payload_post with a non-existent author_id (user):
    payload_post["author_id"] = "qwerty"
    result = requests.post(f"{ENDPOINT}/posts/create", json=payload_post)  # create post
    assert result.status_code == HTTPStatus.NOT_FOUND
    payload_post["author_id"] = result_user.json()["user_id"]

    # the transmitted payload_post with incorrect username:
    payload_post["username"] = "000"
    result = requests.post(f"{ENDPOINT}/users/create", json=payload_post)
    assert result.status_code == HTTPStatus.BAD_REQUEST
    payload_post["username"] = "leo359669"

    # the transmitted payload_post with incorrect email:
    payload_post["email"] = "qwerty"
    result = requests.post(f"{ENDPOINT}/users/create", json=payload_post)
    assert result.status_code == HTTPStatus.BAD_REQUEST
    payload_post["email"] = "test1@test.com"

    # deleting a created user:
    payload_deleting_user_1 = {
        "user_id": result_user.json()["user_id"],
        "password_author": "L5on5don@1",
    }
    delete_user_1 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_1
    )
    assert delete_user_1.status_code == HTTPStatus.OK


def test_get_data_post():
    result_user = requests.post(
        f"{ENDPOINT}/users/create", json=payload_user_1
    )  # create user
    assert result_user.status_code == HTTPStatus.CREATED
    payload_post = {
        "author_id": result_user.json()["user_id"],
        "text": "string",
    }
    result_post = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post
    )  # create post

    # transmitted post_id (post) is an existent:
    result = requests.get(f"{ENDPOINT}/posts/{result_post.json()['post_id']}")
    response = result.json()
    assert result.status_code == HTTPStatus.OK
    assert "post_id" in response
    assert "author_post_name" in response
    assert "author_id" in response
    assert "text" in response
    assert "reactions" in response
    assert "comments" in response

    # transmitted post_id is incorrect or a non-existent:
    result = requests.get(f"{ENDPOINT}/posts/{-1}", json=payload_post)
    assert result.status_code == HTTPStatus.NOT_FOUND

    # deleting a created user:
    payload_deleting_user_1 = {
        "user_id": result_user.json()["user_id"],
        "password_author": "L5on5don@1",
    }
    delete_user_1 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_1
    )
    assert delete_user_1.status_code == HTTPStatus.OK


def test_create_review():
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
    post_id = result_post.json()["post_id"]

    # test - uncorrected reaction has been transmitted:
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "good1",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.BAD_REQUEST
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "good1",
        "comment": "cool!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    assert (
        result_review.text
        == "Reaction is incorrect format.\nComment left successfully."
    )
    comment_id = 0  # comment_id of the first created comment is 0
    assert str(comment_id) in requests.get(f"{ENDPOINT}/posts/comments/all").json()

    # test - a comment and reaction were transmitted:
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "like",
        "comment": "it is cool post!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED
    reaction_id = 0  # reaction_id of the first created reaction is 0
    assert str(reaction_id) in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    comment_id = 1
    assert str(comment_id) in requests.get(f"{ENDPOINT}/posts/comments/all").json()
    # test - only a comment was transmitted:
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "comment": "it is cool post!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED

    #  test - repeated reaction transmitted:
    payload_review = {"author_id": result_user_2.json()["user_id"], "reaction": "boom"}
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.BAD_REQUEST

    #  test - incorrect data was transmitted:
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.BAD_REQUEST
    payload_review = {
        "qwerty": "hello world",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{post_id}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.BAD_REQUEST

    # delete two created users
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


def test_get_posts_sort():
    # create two users:
    result_user_1 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_1)
    assert result_user_1.status_code == HTTPStatus.CREATED
    result_user_2 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_2)
    assert result_user_2.status_code == HTTPStatus.CREATED
    # create post №1 and 3 review:
    payload_post = {"author_id": result_user_1.json()["user_id"], "text": "string"}
    result_post = requests.post(f"{ENDPOINT}/posts/create", json=payload_post)
    assert result_post.status_code == HTTPStatus.CREATED
    post_id_1 = result_post.json()["post_id"]

    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "comment": "cool!",  # 1
    }
    requests.post(f"{ENDPOINT}/posts/{post_id_1}/review", json=payload_review)

    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "like",  # 2
        "comment": "it is cool post!",  # 3
    }
    requests.post(f"{ENDPOINT}/posts/{post_id_1}/review", json=payload_review)

    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "comment": "it is a cool post!",  # 4
    }
    requests.post(f"{ENDPOINT}/posts/{post_id_1}/review", json=payload_review)

    # create post №2 and 1 review:
    payload_post = {
        "author_id": result_user_1.json()["user_id"],
        "text": "hi",
    }
    result_post = requests.post(f"{ENDPOINT}/posts/create", json=payload_post)
    post_id_2 = result_post.json()["post_id"]
    payload_review = {
        "author_id": result_user_2.json()["user_id"],
        "reaction": "like",  # 1
        "comment": "it is a cool post!",  # 2
    }
    requests.post(f"{ENDPOINT}/posts/{post_id_2}/review", json=payload_review)

    # test - uncorrected data has been transmitted:
    payload_sort = {"sort": "asc"}
    result_sort = requests.get(f"{ENDPOINT}/users/{-1}/posts", json=payload_sort)
    assert result_sort.status_code == HTTPStatus.NOT_FOUND

    # test - uncorrected data has been transmitted:
    payload_sort = {"sort": "as"}
    result_sort = requests.get(
        f"{ENDPOINT}/users/{result_user_1.json()['user_id']}/posts", json=payload_sort
    )
    assert result_sort.status_code == HTTPStatus.BAD_REQUEST

    # test - corrected data has been transmitted (asc):
    payload_sort = {"sort": "asc"}
    result_sort = requests.get(
        f"{ENDPOINT}/users/{result_user_1.json()['user_id']}/posts", json=payload_sort
    )
    assert result_sort.status_code == HTTPStatus.OK
    response = result_sort.json()
    assert "posts" in response
    assert (
        len(response["posts"][0]["reactions"]) + len(response["posts"][0]["comments"])
        == 2
    )
    assert (
        len(response["posts"][1]["reactions"]) + len(response["posts"][1]["comments"])
        == 4
    )

    # test - corrected data has been transmitted (desc):
    payload_sort = {"sort": "desc"}
    result_sort = requests.get(
        f"{ENDPOINT}/users/{result_user_1.json()['user_id']}/posts", json=payload_sort
    )
    assert result_sort.status_code == HTTPStatus.OK
    response = result_sort.json()
    assert "posts" in response
    assert (
        len(response["posts"][0]["reactions"]) + len(response["posts"][0]["comments"])
        == 4
    )
    assert (
        len(response["posts"][1]["reactions"]) + len(response["posts"][1]["comments"])
        == 2
    )

    # todo: delete two created users
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
