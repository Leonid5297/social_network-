from app import app, models
from flask import request, Response
import json
from http import HTTPStatus
from datetime import datetime
import collections


@app.post("/posts/create")
def create_post():
    data = request.get_json()
    try:
        author_id = int(data["author_id"])
        text = data["text"]
    except ValueError:
        return Response(status=HTTPStatus.NOT_FOUND)
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = models.Search.get_user_by_id(author_id)
    if not isinstance(user, models.User):
        return user

    if len(models.PostArchive.POSTS) == 0:
        post_id = 0
    else:
        [last] = collections.deque(models.PostArchive.POSTS, maxlen=1)  # last key
        post_id = last + 1
    author_post_name = user.username
    comments = {}
    reactions = {}
    new_post = models.Post(
        post_id, author_post_name, author_id, reactions, text, comments
    )  # creating a new_post
    user.posts[post_id] = new_post  # added  a new Post object  in user.posts
    post_info = new_post.get_info()  # getting info about post (type is dict)
    response = Response(
        json.dumps(post_info), HTTPStatus.CREATED, mimetype="application/json"
    )
    return response


@app.get("/posts/<int:post_id>")
def get_data_post(post_id):
    post = models.Search.get_post_by_post_id(post_id)
    if not isinstance(post, models.Post):
        return post
    data = post.get_info()
    return Response(json.dumps(data), HTTPStatus.OK, mimetype="application/json")


@app.post("/posts/<int:post_id>/review")
def create_review(post_id):
    data = request.get_json()
    text = ""
    # checking the transmitted comment_text:
    flag_comment = False
    try:
        comment_text = data["comment"]
        flag_comment = True
    except KeyError:
        pass  # "comment_text" is  not transmitted

    # checking the transmitted reaction:
    flag_reaction = False
    try:
        reaction = data["reaction"]
        if reaction in ["like", "heart", "dislike", "boom"]:
            flag_reaction = True
        else:
            text += "Reaction is incorrect format.\n"
    except KeyError:
        pass  # "reaction" is  not transmitted or incorrect format

    try:
        author_id = int(data["author_id"])  # author_id commentator
    except Exception:  # if data is not correct type: # KeyError or ValueError
        return Response(status=HTTPStatus.BAD_REQUEST)

    # search in UserArchive commentator (User object):
    commentator_user = models.Search.get_user_by_id(author_id)
    if not isinstance(commentator_user, models.User):
        return commentator_user
    # search in PostArchive the Post object:
    post = models.Search.get_post_by_post_id(post_id)
    if not isinstance(post, models.Post):
        return post

    if flag_reaction is True:
        if models.Reaction.is_repetition_reaction(commentator_user, post):  # it  exists repetition reaction
            flag_reaction = None
            text += "Reaction has already left.\n"

    # work with flags
    if flag_reaction is True and flag_comment is True:
        text += "Comment and reaction left successfully."
    elif flag_reaction is True and flag_comment is False:
        text += "Reaction left successfully."
    elif flag_reaction is False and flag_comment is True:
        text += "Comment left successfully."
    elif flag_reaction is None and flag_comment is True:
        text += "Comment left successfully."
    elif flag_reaction is None and flag_comment is False:
        return Response(text, status=HTTPStatus.BAD_REQUEST, mimetype="text/html")
    elif flag_comment is False and flag_reaction is False:
        text += "Review is not transmitted."
        return Response(text, status=HTTPStatus.BAD_REQUEST, mimetype="text/html")
    # get certain information about the author the review:
    commentator_id = commentator_user.user_id
    commentator_name = commentator_user.username

    # current data:
    date = str(datetime.now())

    # the author of the post:
    author_post = models.Search.get_user_by_id(post.author_id)

    # working with a reaction:
    if flag_reaction:
        if len(models.ReactionArchive.REACTIONS) == 0:
            reaction_id = 0
        else:
            [last] = collections.deque(
                models.ReactionArchive.REACTIONS, maxlen=1
            )  # last key
            reaction_id = last + 1

        reaction_obj = models.Reaction(
            reaction_id, commentator_name, post_id, commentator_id, reaction, date
        )
        author_post.reactions_of_other_users[reaction_id] = reaction_obj
        post.reactions[reaction_id] = reaction_obj
        post.dictionary_reactions[reaction] += 1
        post.history_reactions[commentator_id] = True
        models.ReactionArchive.REACTIONS[reaction_id] = reaction_obj
        commentator_user.history_user_reactions.append(reaction_id)
    # working with a comment:
    if flag_comment:
        if len(models.CommentArchive.COMMENTS) == 0:
            comment_id = 0
        else:
            [last] = collections.deque(models.CommentArchive.COMMENTS, maxlen=1)
            comment_id = last + 1
        comment_obj = models.Comment(
            comment_id, post_id, comment_text, commentator_id, commentator_name, date
        )
        author_post.comments_of_other_users[comment_id] = comment_obj
        post.comments[comment_id] = comment_obj
        models.CommentArchive.COMMENTS[comment_id] = comment_obj
        commentator_user.history_user_comments.append(comment_id)
    return Response(text, status=HTTPStatus.CREATED, mimetype="text/html")


@app.get("/users/<int:user_id>/posts")
def get_posts_sort(user_id):
    data = request.get_json()
    try:
        sort = data["sort"]
    except KeyError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    if sort == "asc" or sort == "desc":
        user = models.Search.get_user_by_id(user_id)
        if isinstance(user, models.User):
            user_posts = user.posts
            user_posts_new = []
            for obj in user_posts:  # for in  post id of user posts
                post = user_posts[obj]
                user_posts_new.append(
                    (post.count_reactions_and_comments(), post.get_info())
                )

            user_posts_new = (
                sorted(user_posts_new, key=lambda row: row[0])
                if sort == "asc"
                else sorted(user_posts_new, key=lambda row: row[0], reverse=True)
            )
            user_posts_sort = []
            for post in user_posts_new:
                user_posts_sort.append(post[1])
            dict_posts_sort = {"posts": user_posts_sort}

            return dict_posts_sort, 200, {"content-type": "application/json"}
        else:
            return user
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)


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
    if not isinstance(user, models.User):
        return user
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
    if not isinstance(reaction, models.Reaction):
        return reaction

    author_reaction = models.Search.get_user_by_reaction_id(reaction_id)
    if not isinstance(author_reaction, models.User):
        return author_reaction
    if password != author_reaction.password:
        return Response(status=HTTPStatus.BAD_REQUEST)

    post = models.Search.get_post_by_reaction_id(reaction_id)
    author_post = models.Search.get_user_by_post_id(post.post_id)  # User-object

    if not isinstance(author_post, models.User):
        return author_post
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
    if not isinstance(comment, models.Comment):
        return comment

    author_comment = models.Search.get_user_by_comment_id(comment_id)
    if not isinstance(author_comment, models.User):
        return author_comment
    if password != author_comment.password:
        return Response(status=HTTPStatus.BAD_REQUEST)

    post = models.Search.get_post_by_comment_id(comment_id)
    author_post = models.Search.get_user_by_post_id(post.post_id)

    if not isinstance(post,models.Post):
        return post
    comment.delete(post, author_post)
    return Response(status=HTTPStatus.OK)
