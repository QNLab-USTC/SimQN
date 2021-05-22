"""
The classic network model for sending and receiving classic message.
"""

from .link import ClassicLink, ClassicLinkProtocol
from .node import ClassicNode, ClassicRecvProtocol, ClassicSendProtocol, ClassicSwitchProtocol
from .message import Message
