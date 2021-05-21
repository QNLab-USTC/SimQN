import uuid

class Message(object):
    def __init__(self, content, from_node, to_node, link = None):
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