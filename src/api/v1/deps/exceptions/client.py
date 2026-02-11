from fastapi import HTTPException, status


class ClientNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )


class ClientExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_410_GONE,
            detail="Client subscription has expired",
        )
