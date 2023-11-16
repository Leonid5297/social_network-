from app import app, models
from flask import request, Response
from http import HTTPStatus


@app.delete("/users/delete/user")
def delete_user():
    data = request.get_json()
    try:
        user_id = int(data["user_id"])  # a string is allowed if it consists of digits
        password = data["password_author"]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    except ValueError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = models.Search.get_user_by_id(user_id)
    if user is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    if password != user.password:
        return Response(status=HTTPStatus.BAD_REQUEST)
    user.delete()
    return Response(status=HTTPStatus.OK)


@app.delete("/users/delete/post")
def delete_post():
    data = request.get_json()
    try:
        user_id = int(data["author_id"])  # a string is allowed if it consists of digits
        password = data["password_author"]
        post_id = int(data["post_id"])

    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    except ValueError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = models.Search.get_user_by_id(user_id)
    if user is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    if password != user.password:
        return Response(status=HTTPStatus.BAD_REQUEST)
    try:
        post = user.posts[post_id]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    post.delete(user)
    return Response(status=HTTPStatus.OK)


@app.delete("/users/delete/reaction")
def delete_reaction():
    data = request.get_json()
    try:
        reaction_id = int(
            data["reaction_id"]
        )  # a string is allowed if it consists of digits
        password = data["password_author"]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    except ValueError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    reaction = models.Search.get_reaction_by_reaction_id(reaction_id)
    if reaction is None:
        return Response(status=HTTPStatus.NOT_FOUND)

    author_reaction = models.Search.get_user_by_reaction_id(reaction_id)
    if author_reaction is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    if password != author_reaction.password:
        return Response(status=HTTPStatus.BAD_REQUEST)

    post = models.Search.get_post_by_reaction_id(reaction_id)
    author_post = models.Search.get_user_by_post_id(post.post_id)  # User-object

    if post is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    reaction.delete(post, author_post)
    return Response(status=HTTPStatus.OK)


@app.delete("/users/delete/comment")
def delete_comment():
    data = request.get_json()
    try:
        comment_id = int(
            data["comment_id"]
        )
        password = data["password_author"]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    except ValueError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    comment = models.Search.get_comment_by_comment_id(comment_id)
    if comment is None:
        return Response(status=HTTPStatus.NOT_FOUND)

    author_comment = models.Search.get_user_by_comment_id(comment_id)
    if author_comment is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    if password != author_comment.password:
        return Response(status=HTTPStatus.BAD_REQUEST)

    post = models.Search.get_post_by_comment_id(comment_id)
    author_post = models.Search.get_user_by_post_id(post.post_id)

    if post is None:
        return Response(status=HTTPStatus.NOT_FOUND)
    comment.delete(post, author_post)
    return Response(status=HTTPStatus.OK)
