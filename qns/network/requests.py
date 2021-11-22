from typing import Dict

class Request():
    """
    A request is a source-destination pair represents a quantum transmitting request.
    """

    def __init__(self, src, dest, attr: Dict = {}) -> None:
        """
        Args:
            src: the source node
            dest: the destination node
            attr: other attributions
        """
        from qns.entity import QNode
        self.src: QNode = src
        self.dest: QNode = dest
        self.attr: Dict = attr

    def __repr__(self) -> str:
        return f"<Request {self.src}->{self.dest}>"