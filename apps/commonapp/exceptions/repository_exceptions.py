from .base import AppError

class RepositoryError(AppError):
    default_message="A repository error occured"

class NotFoundError(RepositoryError):
    default_message="Requested resource was not found"