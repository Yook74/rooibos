class NakResponse(Exception):
    """Raised when the ECM responds with a NAK instead of an ACK"""


class UnknownResponse(Exception):
    """Raised when the driver code can't interpret the ECM's response"""
