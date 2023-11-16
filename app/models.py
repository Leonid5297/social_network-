import re
import copy
from abc import ABC, abstractmethod


class ValidationError(Exception):
    """Raises when password (or email) is not valid."""


class ObjectSocialNetwork(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def delete(self, *args):
        pass


class Archive(ABC):
    @staticmethod
    @abstractmethod
    def _entry(self):
        pass


# archives of social network objects:
class UserArchive(Archive):
    USERS = {}
    USERNAME = {}

    @staticmethod
    def _entry(user):
        UserArchive.USERS[user.user_id] = user
        UserArchive.USERNAME[user.username] = True


class PostArchive(Archive):
    POSTS = {}

    @staticmethod
    def _entry(post):
        PostArchive.POSTS[post.post_id] = post


class ReactionArchive(Archive):
    REACTIONS = {}

    @staticmethod
    def _entry(reaction):
        ReactionArchive.REACTIONS[reaction.reaction_id] = reaction


class CommentArchive(Archive):
    COMMENTS = {}

    @staticmethod
    def _entry(comment):
        CommentArchive.COMMENTS[comment.comment_id] = comment


# social network objects:
class User(ObjectSocialNetwork, UserArchive):
    def __init__(
            self,
            user_id,
            username,
            email,
            password,
            comments_of_other_users,
            reactions_of_other_users,
            posts,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.__password = password
        self.comments_of_other_users = (
            comments_of_other_users  # other people's reaction to certain user posts
        )
        self.reactions_of_other_users = reactions_of_other_users
        self.posts = posts  # dict of Post-objects
        self.history_user_reactions = []
        self.history_user_comments = []
        super()._entry(self)

    def get_info(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "comments_of_other_users": [
                self.comments_of_other_users[obj].get_info()
                for obj in self.comments_of_other_users
            ],
            "reactions_of_other_users": [
                self.reactions_of_other_users[obj].get_info()
                for obj in self.reactions_of_other_users
            ],
            "posts": [self.posts[obj].get_info() for obj in self.posts],
        }

    def delete(self):
        # deleting a comments and reactions of user, he has ever left on posts of other users
        for comment_id in self.history_user_comments:
            comment = Search.get_comment_by_comment_id(comment_id)
            post = Search.get_post_by_comment_id(comment_id)
            author_post = Search.get_user_by_post_id(post.post_id)
            comment.delete(post, author_post)
        for reaction_id in self.history_user_reactions:
            reaction = Search.get_reaction_by_reaction_id(reaction_id)
            post = Search.get_post_by_reaction_id(reaction_id)
            author_post = Search.get_user_by_post_id(post.post_id)
            reaction.delete(post, author_post)
        flag = True  # it means that the user is being deleted now
        posts = copy.deepcopy(self.posts)
        for pst in posts:  # deleting all posts of user
            self.posts[pst].delete(self, flag)
        del UserArchive.USERS[self.user_id]
        del UserArchive.USERNAME[self.username]
        del posts
        del self

    @property
    def password(self):
        return self.__password

    @staticmethod
    def is_valid_password(password):
        # Checks for the presence of characters in both registers,
        # numbers, special characters and a minimum length of 8 characters
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )
        if re.match(pattern, password) is None:
            raise ValidationError(
                """Password has incorrect format. Checks for the presence of characters in both registers,
            numbers, special characters and a minimum length of 8 characters. 
            The password can contain only letters of the Latin alphabet, numbers, special characters."""
            )

    @staticmethod
    def is_valid_email(email):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) is None:
            raise ValidationError("Email has incorrect format.")

    @staticmethod
    def is_valid_name(username):
        conditions = []
        count_mistakes = 0
        if username in UserArchive.USERNAME:
            conditions.append("The user with the same name already exists.")
            count_mistakes += 1
        if not (5 < len(username) < 13):
            conditions.append(
                "The length of the username must be more than five and be less than thirteen."
            )
            count_mistakes += 1

        if not ((64 < ord(username[0]) < 91) or (96 < ord(username[0]) < 123)):
            conditions.append("The name must begin with a Latin letter.")
            count_mistakes += 1

        count_of_special_characters = 0
        flag = False
        for sb in username[1:]:
            symbol = ord(sb)
            if (32 < symbol < 48) or (57 < symbol < 65) or (90 < symbol < 97):
                count_of_special_characters += 1
                if count_of_special_characters > 3:
                    conditions.append(
                        "The name must contain no more than 3 special characters."
                    )
                    count_mistakes += 1
            elif (
                    not ((47 < symbol < 58) or (64 < symbol < 91) or (96 < symbol < 123))
                    and flag is False
            ):
                conditions.append(
                    "The name can contain only letters of the Latin alphabet, numbers, special characters."
                )
                count_mistakes += 1
                flag = True
        if len(conditions) == 0:
            return True, ""
        else:
            mistakes = ""
            for err in conditions:
                mistakes += "\n" + err
            return (
                False,
                f"<h4>{count_mistakes} {'errors' if count_mistakes > 1 else 'error'} found in the submitted username:</h4>{mistakes}",
            )


class Post(ObjectSocialNetwork, PostArchive):
    def __init__(self, post_id, author_post_name, author_id, reactions, text, comments):
        self.post_id = post_id
        self.author_post_name = author_post_name
        self.author_id = author_id
        self.text = text
        self.reactions = reactions
        self.dictionary_reactions = {"heart": 0, "like": 0, "dislike": 0, "boom": 0}
        self.comments = comments
        self.history_reactions = {}
        super()._entry(self)

    def get_info(self):
        return {
            "post_id": self.post_id,
            "author_post_name": self.author_post_name,
            "author_id": self.author_id,
            "text": self.text,
            "reactions": [self.reactions[rct].get_info() for rct in self.reactions],
            "comments": [self.comments[cmt].get_info() for cmt in self.comments],
        }

    def delete(self, author_post, flag=False):
        # if flag is False => deleting a comment or deleting a post
        comments = copy.deepcopy(self.comments)
        for cmt in comments:  # deleting all user comments
            self.comments[cmt].delete(post=None, author_post=author_post, flag=flag)
        reactions = copy.deepcopy(self.reactions)
        for rct in reactions:  # deleting all user comments
            self.reactions[rct].delete(post=None, author_post=author_post, flag=flag)
        del PostArchive.POSTS[self.post_id]
        del author_post.posts[self.post_id]
        del comments
        del reactions
        del self  # deleting post-object

    def count_reactions_and_comments(self):
        return len(self.comments) + len(self.reactions)


class Comment(ObjectSocialNetwork, CommentArchive):
    def __init__(
            self, comment_id, post_id, text, author_comment_id, commentator_name, date
    ):
        self.comment_id = comment_id
        self.post_id = post_id
        self.text = text
        self.author_comment_id = author_comment_id
        self.commentator_name = commentator_name
        self.date = date
        super()._entry(self)

    def get_info(self):
        return {
            "comment_id": self.comment_id,
            "author_comment_name": self.commentator_name,
            "post_id": self.post_id,
            "author_comment_id": self.author_comment_id,
            "text": self.text,
            "date": self.date,
        }

    def delete(self, post, author_post, flag=False):
        if not (post is None):
            del post.comments[self.comment_id]
        if flag is False:
            del author_post.comments_of_other_users[self.comment_id]
        author_comment = Search.get_user_by_comment_id(self.comment_id)
        author_comment.history_user_comments.remove(self.comment_id)

        del CommentArchive.COMMENTS[self.comment_id]
        del self  # deleting Comments-object


class Reaction(ObjectSocialNetwork, ReactionArchive):
    def __init__(
            self, reaction_id, commentator_name, post_id, author_reaction_id, reaction, date
    ):
        self.reaction_id = reaction_id
        self.commentator_name = commentator_name
        self.post_id = post_id
        self.author_reaction_id = author_reaction_id
        self.reaction = reaction
        self.date = date
        super()._entry(self)

    def get_info(self):
        return {
            "reaction_id": self.reaction_id,
            "author_reaction_name": self.commentator_name,
            "post_id": self.post_id,
            "author_reaction_id": self.author_reaction_id,
            "reaction": self.reaction,
            "date": self.date,
        }

    def delete(self, post, author_post, flag=False):
        if not (post is None):
            post.dictionary_reactions[self.reaction] -= 1
            author_reaction = Search.get_user_by_reaction_id(self.reaction_id)
            del post.history_reactions[author_reaction.user_id]
            del post.reactions[self.reaction_id]
        if flag is False:
            del author_post.reactions_of_other_users[self.reaction_id]
        author_reaction = Search.get_user_by_reaction_id(self.reaction_id)
        author_reaction.history_user_reactions.remove(self.reaction_id)
        del ReactionArchive.REACTIONS[self.reaction_id]
        del self  # deleting Reaction-object

    @staticmethod
    def is_repetition_reaction(user, post):
        try:
            d = post.history_reactions[user.user_id]
            return True  # reaction has already left this user
        except KeyError:
            return False


class Search:  # Search objects in Archives by object-id
    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = UserArchive.USERS[user_id]
        except KeyError:
            return None
        return user  # certain  User object

    @staticmethod
    def get_user_by_post_id(post_id):
        try:
            post = PostArchive.POSTS[post_id]
            user = UserArchive.USERS[post.author_id]
        except KeyError:
            return None
        return user  # certain  User object

    @staticmethod
    def get_post_by_post_id(post_id):
        try:
            post = PostArchive.POSTS[post_id]
        except KeyError:
            return None
        return post

    @staticmethod
    def get_post_by_comment_id(comment_id):
        try:
            comment = CommentArchive.COMMENTS[comment_id]
            post = PostArchive.POSTS[comment.post_id]
        except KeyError:
            return None
        return post

    @staticmethod
    def get_post_by_reaction_id(reaction_id):
        try:
            reaction = ReactionArchive.REACTIONS[reaction_id]
            post = PostArchive.POSTS[reaction.post_id]
        except KeyError:
            return None
        return post

    @staticmethod
    def get_user_by_comment_id(comment_id):
        try:
            comment = CommentArchive.COMMENTS[comment_id]
            user = UserArchive.USERS[comment.author_comment_id]
        except KeyError:
            return None
        return user

    @staticmethod
    def get_user_by_reaction_id(reaction_id):
        try:
            reaction = ReactionArchive.REACTIONS[reaction_id]
            user = UserArchive.USERS[reaction.author_reaction_id]
        except KeyError:
            return None
        return user

    @staticmethod
    def get_reaction_by_reaction_id(reaction_id):
        try:
            reaction = ReactionArchive.REACTIONS[reaction_id]
        except KeyError:
            return None
        return reaction

    @staticmethod
    def get_comment_by_comment_id(comment_id):
        try:
            comment = CommentArchive.COMMENTS[comment_id]
        except KeyError:
            return None
        return comment

