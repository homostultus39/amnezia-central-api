from fastapi import HTTPException, status


class InvalidTokenException(HTTPException):
    """Invalid or expired token exception."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenNotProvidedException(HTTPException):
    """Token not provided exception."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(HTTPException):
    """Invalid credentials exception."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
