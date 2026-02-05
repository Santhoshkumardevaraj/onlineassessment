from .base import AppError


class ServiceError(AppError):
    default_message = "A repository error occured"


class NotFoundError(ServiceError):
    default_message = "Requested resource was not found"
