from fastapi import HTTPException, status


class ClusterNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )


class ClusterAuthException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid cluster API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


class ClusterAPIException(HTTPException):
    def __init__(self, detail: str = "Cluster API error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
