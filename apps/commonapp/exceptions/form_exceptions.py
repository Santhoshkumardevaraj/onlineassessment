from .base import AppError


class FormError(AppError):
    default_message = "A Form error occured"


class NotFoundError(FormError):
    default_message = "Requested resource was not found"
