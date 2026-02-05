import logging
import traceback
from datetime import datetime

logger = logging.getLogger("django")


class AppError(Exception):
    default_message = "An unexpected error occured"

    def __init__(
        self, message=None, log=True, extra=None, original_exception=None, *args
    ):
        if message is None:
            message = self.default_message
        self.message = "ERROR: " + message
        self.original_exception = original_exception  # store original exception
        super().__init__(message, *args)

        if log:
            self.log_exception(extra)

    def log_exception(self, extra=None):
        log_data = (
            f"\n\n##### ERROR {datetime.now().strftime('%Y-%B-%d %H:%M:%S:%f')} #####\n"
            f"Exception Type: {type(self).__name__}\n"
            f"Message: {self.message}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
        )

        if self.original_exception:
            log_data += f"Original Exception: {repr(self.original_exception)}\n"

        if extra:
            log_data += f"Extra Context: {extra}\n"
        log_data += "\n**** END OF CURRENT EXCEPTION DETAILS ****\n\n"
        logger.error(log_data)
