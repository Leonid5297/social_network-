from app import app
from app import models
from flask import Response
import json
from http import HTTPStatus


@app.get("/users/all")
def get_user_archive():
    users = {}
    for obj in models.UserArchive.USERS:
        users[obj] = models.UserArchive.USERS[obj].get_info()
    return Response(json.dumps(users), status=HTTPStatus.OK, mimetype="application/json")


@app.get("/posts/all")
def get_post_archive():
    posts = {}
    for obj in models.PostArchive.POSTS:
        posts[obj] = models.PostArchive.POSTS[obj].get_info()
    return Response(json.dumps(posts), status=HTTPStatus.OK, mimetype="application/json")


@app.get("/posts/reactions/all")
def get_reaction_archive():
    reactions = {}
    for obj in models.ReactionArchive.REACTIONS:
        reactions[obj] = models.ReactionArchive.REACTIONS[obj].get_info()
    return Response(json.dumps(reactions), status=HTTPStatus.OK, mimetype="application/json")


@app.get("/posts/comments/all")
def get_comment_archive():
    comments = {}
    for obj in models.CommentArchive.COMMENTS:
        comments[obj] = models.CommentArchive.COMMENTS[obj].get_info()
    return Response(json.dumps(comments), status=HTTPStatus.OK, mimetype="application/json")
