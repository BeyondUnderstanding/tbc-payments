from requests import Response


class FailedRequest(Exception):
    def __init__(self, message, details):
        self.message = None
        self.details: Response | None = None
        super().__init__(self.message)
