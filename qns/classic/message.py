
class Message(object):
    def __init__(self, content):
        self.content = content

    def __len__(self):
        try:
            return len(self.content)
        except TypeError:
            return 1

    def __repr__(self):
        return f"<message: {self.content}>"