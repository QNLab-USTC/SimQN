class QStateSizeNotMatchError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass


class QStateQubitNotInStateError(Exception):
    pass


class OperatorNotMatchError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass


class QStateBaseError(Exception):
    pass
