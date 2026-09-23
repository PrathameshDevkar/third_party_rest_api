class APIError(Exception):
    """
    Base exception for all API errors.
    Every other api error inherits from this.

    Why base class?
    Callers can either catch specific errors (RateLimitError) or
    caller can catch all errors at once (APIError). Both work.

    catch specific:
        except RateLimitError -> only rate limit error

    catch all APIError:
        except APIError -> catches any of the subclasses below
    """
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        return (
            f"{self.__class__.__name__} | "
            f"status={self.status_code} | "
            f"message={super().__str__()}"
        )


class NetworkError(APIError):
    """
    Raised when the request never reaches the server.
    Examples:
    - No internet connection
    - DNS lookup failed
    - Connection timed out waiting for server to respond
    These are safe to retry- The server never saw the request.
    """
    pass

class AuthenticationError(APIError):
    """
    Raised on 401 Unauthentication.
    Means: your token is missing, wrong or expired.
    Dont retry, fix your token first
    """
    pass

class AuthorizationError(APIError):
    """
    Raised on 403 Unauthorized/ forbidden.
    Means: your token is valid but doesn't have permission
    ex- reading a private repo with a public-only token.
    Do not retry - you need a different token scope
    """
    pass

class NotFoundError(APIError):
    """
    Raised on 404 error.
    Means: the resource doesnt exist.
    Do not retry- it wont appear magically
    """
    pass

class ValidationError(APIError):
    """
    Raised on 400 Bad request or 422 Unprocessable.
    Means: you sent invalid data.
    Do not retry - Fix your request payload first.
    """
    pass

class RateLimitError(APIError):
    """
    Raised on 429 to many request.
    Means: You have exhausted the allowed request rate.
    Safe to retry - But only after waiting retry_after seconds.

    retry_after: seconds to wait before retrying
                 comes from retry-after response header
    """
    def __init__(self, message: str, retry_after: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

    def __str__(self):
        return (
            f"{super().__str__()} | "
            f"retry _after={self.retry_after} |"
        )
    
class ServerError(APIError):
    """
    Raised on 5xx Server Errors.
    Means: the github server crashed or overloaded
    Safe to retry - the problem is on their side
    """
    pass

class UnexpectedResponseError(APIError):
    """
    Raised when response status code is something we didnt expect.
    cathes anything that slips through the otehr cases.
    """
    pass
