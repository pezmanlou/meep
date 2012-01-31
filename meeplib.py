"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
     is a guaranteed unique integer reference.

 * m = Message(title, post, author, reply) - creates & saves a Message object.
     'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""

__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
           'User', 'get_user', 'get_all_users', 'delete_user']

###
# internal data structures & functions; please don't access these
# directly from outside the module.  Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

def _get_next_message_id():
    if _messages:
        return max(_messages.keys()) + 1
    return 0

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

def _get_max_user_id():
    if _users:
        return max(_user_ids.keys())
    return 0

def _get_next_user_id():
    if _users:
        max_user_id = _get_max_user_id()
        return max_user_id + 1
    return 0

def _reset():
    """
    Clean out all persistent data structures, for testing purposes.
    """
    global _messages, _users, _user_ids
    _messages = {}
    _users = {}
    _user_ids = {}


# Class: Message
# Usage: Message(title, post, author, reply)
#   title - The title of the Message
#   post - The content of the Message
#   author - The username of the creator of the Message
#   reply - The ID of the Message that this Message is replying to.  ID 0 is 
#           the id of the root message.  Use -1 for a Message that is not in
#           reply to another Message.
#
# Example: Message("Hi", "what's up, friends?", billyEveryTeen, -1)

class Message(object):
    """
    Simple "Message" object, containing title/post/author.

    'author' must be an object of type 'User'.
    
    """
    def __init__(self, title, post, author, reply=-1):
        self.title = title
        self.post = post
        self.reply_to = reply
        self.id = _get_next_message_id()

        assert isinstance(author, User)
        self.author = author

        self._save_message()
        print "+M:", self.id, self.reply_to, self.title, self.post

    def _save_message(self):
        
        # register this new message with the messages list:
        _messages[self.id] = self

def get_all_messages(sort_by='id'):
    return _messages.values()

def get_message(id):
    return _messages[int(id)]


def delete_message(msg):
    assert isinstance(msg, Message)
    print "-M:", msg.id, msg.reply_to, msg.title, msg.post
    del _messages[msg.id]


###

class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self._save_user()

    def _save_user(self):
        self.id = _get_next_user_id()

        # register new user ID with the users list:
        _user_ids[self.id] = self
        _users[self.username] = self

def get_user(username):
    return _users.get(username)         # return None if no such user

def get_all_users():
    return _users.values()

def delete_user(user):
    del _users[user.username]
    del _user_ids[user.id]
