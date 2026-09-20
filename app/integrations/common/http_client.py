import httpx

from .exceptions import (
    RateLimitError,
    AuthenticationError,
    ExernalAPIError
)

class HTTPClient:
    def __init__(
        self, 
        base_url:str,
        timeout:float = 10
    )