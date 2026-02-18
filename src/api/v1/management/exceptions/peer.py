from fastapi import HTTPException, status


class PeerNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )


class PeerAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Peer with this public key already exists",
        )


class PeerDuplicateAppTypeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Peer with this app_type already exists for this client on this cluster",
        )
