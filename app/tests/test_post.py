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

    # deleting two created users
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


def test_delete_post():
    # creating the user_1 and the user_2
    result_user_1 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_1)
    assert result_user_1.status_code == HTTPStatus.CREATED
    result_user_2 = requests.post(f"{ENDPOINT}/users/create", json=payload_user_2)
    assert result_user_2.status_code == HTTPStatus.CREATED

    # creating the post of user_1
    payload_post = {
        "author_id": result_user_1.json()["user_id"],
        "text": "string",
    }
    result_post = requests.post(
        f"{ENDPOINT}/posts/create", json=payload_post
    )
    assert result_post.status_code == HTTPStatus.CREATED
    # creating reaction and  comment of user_2 on post of user_1:
    payload_review = {
        "author_id": result_user_2.json()["user_id"],  # user_2 - author of the reaction
        "reaction": "like",
        "comment": "cool!",
    }
    result_review = requests.post(
        f"{ENDPOINT}/posts/{result_post.json()['post_id']}/review", json=payload_review
    )
    assert result_review.status_code == HTTPStatus.CREATED

    # Test - deleting of post:
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
    )  # reactions of this post  must be missing from the ReactionArchive
    assert (
            "0" not in requests.get(f"{ENDPOINT}/posts/reactions/all").json()
    )  # comment of this post must be missing from the CommentArchive

    # deleting of users:
    assert result_review.status_code == HTTPStatus.CREATED
    payload_deleting_user_1 = {
        "user_id": result_user_1.json()["user_id"],
        "password_author": "L5on5don@1",
    }  # for user_1
    result_deleting_user_1 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_1
    )
    assert result_deleting_user_1.status_code == HTTPStatus.OK

    payload_deleting_user_2 = {
        "user_id": result_user_2.json()["user_id"],
        "password_author": "Lnt32kfa@",
    }  # for user_2
    delete_user_2 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_2
    )
    assert delete_user_2.status_code == HTTPStatus.OK


def test_delete_review():
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
    )  # create post (user_1)
    assert result_post.status_code == HTTPStatus.CREATED

    # creating of the reaction and the comment of user_2 on post of user_1:
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

    # Test - deleting reaction and comment:
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

    # deleting of users:
    payload_deleting_user_1 = {
        "user_id": result_user_1.json()["user_id"],
        "password_author": "L5on5don@1",
    }  # for user_1
    result_deleting_user_1 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_1
    )
    assert result_deleting_user_1.status_code == HTTPStatus.OK

    payload_deleting_user_2 = {
        "user_id": result_user_2.json()["user_id"],
        "password_author": "Lnt32kfa@",
    }  # for user_2
    delete_user_2 = requests.delete(
        f"{ENDPOINT}/users/delete/user", json=payload_deleting_user_2
    )
    assert delete_user_2.status_code == HTTPStatus.OK
