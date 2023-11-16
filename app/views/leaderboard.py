from app import app, models
from flask import request, Response
import json
from http import HTTPStatus
import matplotlib.pyplot as plt
import numpy as np


@app.get("/users/leaderboard")
def leader_board():
    data = request.get_json()

    # checking the correctness of the transmitted
    try:
        sort = data["sort"]
        assert sort in ["asc", "desc"]
    except Exception:  # KeyError and AssertionError
        sort = None

    try:
        type_data = data["type"]
        assert type_data in ["graph", "list"]
    except AssertionError:
        return Response(status=HTTPStatus.BAD_REQUEST)
    except KeyError:
        type_data = None

    # sorted by count comments and reactions
    if not (type_data is None):
        list_users = []
        for self in models.UserArchive.USERS:
            user = models.UserArchive.USERS[self]
            list_users.append(
                (
                    len(user.comments_of_other_users)
                    + len(user.reactions_of_other_users),
                    user.user_id,
                    user.username,
                )
            )

        if not (sort is None):
            # sorting users by the count of reactions and comments:
            list_users = (
                sorted(list_users, key=lambda row: row[0])
                if sort == "asc"
                else sorted(list_users, key=lambda row: row[0], reverse=True)
            )
            # type_data recognition:
            if type_data == "list":
                dict_users = {"users": []}
                for cort in list_users:
                    dict_users["users"].append(
                        {
                            "count_reactions": cort[0],
                            "user_id": cort[1],
                            "username": cort[2],
                        }
                    )
                return Response(
                    json.dumps(dict_users),
                    status=HTTPStatus.OK,
                    mimetype="application/json",
                )

            else:  # return graph with sorted data
                count_of_reactions = []
                user_names = []
                for t in list_users:
                    count_of_reactions.append(t[0])
                    user_names.append(t[2])  # (user_name)
                fig, ax = plt.subplots()
                ax.bar(np.arange(len(user_names)), count_of_reactions)
                plt.xticks(ticks=np.arange(len(user_names)), labels=user_names, rotation=-55)
                plt.yticks(ticks=count_of_reactions)
                ax.set_ylabel('Count of reactions')
                ax.set_title("Graph of users by number of reactions", fontname="impact")
                plt.savefig(fname="app/static/users_leaderboard.png")
                return Response(
                    "<img src='/static/users_leaderboard.png'>",
                    status=HTTPStatus.OK,
                    mimetype="text/html",
                )

        elif type_data == "graph":
            # return a usual graph (without sorting)
            count_of_reactions = []
            user_names = []
            for t in list_users:
                count_of_reactions.append(t[0])
                user_names.append(t[2])  # (user_name)
            fig, ax = plt.subplots()
            ax.bar(np.arange(len(user_names)), count_of_reactions)
            plt.xticks(ticks=np.arange(len(user_names)), labels=user_names, rotation=-55)
            plt.yticks(ticks=count_of_reactions)
            ax.set_ylabel('Count of reactions')
            ax.set_title("Graph of users by number of reactions", fontname="impact")
            plt.savefig(fname="app/static/users_leaderboard.png")
            return Response(
                "<img src='/static/users_leaderboard.png'>",
                status=HTTPStatus.OK,
                mimetype="text/html",
            )

        else:
            # return a usual list (without sorting)
            list_users = [
                (
                    len(models.UserArchive.USERS[self].comments_of_other_users)
                    + len(models.UserArchive.USERS[self].reactions_of_other_users),
                    models.UserArchive.USERS[self].user_id,
                )
                for self in models.UserArchive.USERS
            ]
            dict_users = {"users": []}
            for cort in list_users:
                dict_users["users"].append(
                    {"count_reactions": cort[0], "user_id": cort[1]}
                )
            return Response(
                json.dumps(dict_users),
                status=HTTPStatus.OK,
                mimetype="application/json",
            )
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)
