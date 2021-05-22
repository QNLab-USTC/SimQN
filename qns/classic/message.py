import uuid


class Message(object):
    '''
    This class presents a classic message.

    If the ``content`` is a string or a list, its ``length`` will be used to present the package size.
    Otherwise, the package size will be set to ``1``.

    :param content: the real message content
    :param from_node: the message sender
    :param to_node: the message recevier
    :param link: the first link which the ``from_node`` will put this message into
    '''

    def __init__(self, content, from_node, to_node, link=None):
        self.content = content
        self.from_node = from_node
        self.to_node = to_node
        self.link = link
        self.name = uuid.uuid4()

    def __len__(self):
        try:
            return len(self.content)
        except TypeError:
            return 1

    def __repr__(self):
        return f"<message: {self.name} \"{self.content}\" from {self.from_node} to {self.to_node}>"
