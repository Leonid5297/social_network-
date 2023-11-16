from app import app, models
from flask import request, Response
import json
from http import HTTPStatus
import collections


@app.post("/users/create")
def create_user():
    data = (
        request.get_json()
    )  # post request from user => "username" ,"email", password

    try:
        username = data["username"]
        email = data["email"]
        password = data["password"]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    validity_value = models.User.is_valid_name(username)
    if validity_value[0] is False:
        return Response(validity_value[1], status=HTTPStatus.BAD_REQUEST, mimetype="text/html")

    try:
        models.User.is_valid_password(password)
        models.User.is_valid_email(email)
    except models.ValidationError as text:
        return Response(str(text), status=HTTPStatus.BAD_REQUEST, mimetype="text/html")

    comments_of_other_users = {}
    posts = {}
    reactions_of_other_users = {}
    if len(models.UserArchive.USERS) == 0:
        user_id = 0
    else:
        [last] = collections.deque(models.UserArchive.USERS, maxlen=1)  # last key
        user_id = last + 1
    # registration user and entry in archive:
    user = models.User(
        user_id,
        username,
        email,
        password,
        comments_of_other_users,
        reactions_of_other_users,
        posts,
    )
    user_dict = (
        user.get_info()
    )  # getting info about certain user (type - dictionary)
    models.UserArchive.USERNAME[username] = True
    return Response(
        json.dumps(user_dict), HTTPStatus.CREATED, mimetype="application/json"
    )


@app.get("/users/<int:user_id>")  # need test
def get_data_user(user_id):
    user = models.Search.get_user_by_id(user_id)
    if user is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    return Response(
        json.dumps(user.get_info()), HTTPStatus.OK, mimetype="application/json"
    )


