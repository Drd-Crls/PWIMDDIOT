class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class NotFoundError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class DatabaseError(AppException):
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status_code=500)
