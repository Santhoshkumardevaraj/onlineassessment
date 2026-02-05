from .base import AppError


class ViewError(AppError):
    default_message = "A View error occured"


class NotFoundError(ViewError):
    default_message = "Requested resource was not found"
