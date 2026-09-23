import os
import logging 
import requests
from dotenv import load_dotenv
from .exceptions import (
    NetworkError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    UnexpectedResponseError
)

load_dotenv()

#logging gives timestamps, severity level and can be turned off in the production
logging.basicConfig(
    level = logging.DEBUG,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

class BaseAPIClient:
    """
    Generic rest api client.

    Holds shared state (base_url, session, timeout) and provides
    a single .request() method that all subclasses use.

    why session instead of requests.get() ->
    - Session reuses TCP connection
    - Session lets you set default headers once
    - Session gives you cookie persistance if needed
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """
        base url: root url ,for example- https://api.github.com
        timeout: seconds to wait before giving up on the request    
                always set this- without this the code can 
                hang forever if the server stops responding.
        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        logging.debug(
            "BaseAPIClient initialized | base_url= %s | timeout= %s",
            self.base_url,
            self.timeout
        )

    def _get_headers(self) -> dict :
        """
        returns headers to include in every request.

        This method is meant to be overridden in the subclass.
        The base version remain empty dict, the subclasses add auth headers.

        The leading underscore on _get_headers means:
        "This is an internal method, not part of public API"
        """

        return {}

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Inspect the response status code and raises the correct exception.
        Called only when the status code is NOT SUCCESS (not 2xx).

        We raised instead of returning, because the errors should
        interrupt the normal flow , not silently passed up
        """
        status = response.status_code

        # Try to get error message from response body
        # API usually put a helpful message in the JSON body
        try:
            body = response.json()
            # Github puts the message in the body["message"]
            api_message = body.get("message", response.text)
        except Exception:
            # Response body wasn't json - use raw text
            api_message = response.text

        logging.error(
            "API error | status= %s | error_message= %s",
            status,
            api_message
        )

        if status == 401:
            raise AuthenticationError(
                f"Authentication failed: {api_message}",
                status_code= status,
                response_body = response.text
            )
        
        elif status == 403:
            raise AuthorizationError(
                f"Permission denied: {api_message}",
                status_code = status,
                response_body = response.text
            )
        
        elif status == 404:
            raise NotFoundError(
                f"Resource not found: {api_message}",
                status_code = status,
                response_body = response.text
            )

        elif status in (400,422):
            raise ValidationError(
                f"Invalid request: {api_message}",
                status_code = status,
                response_body = response.text
            )
        
        elif status == 429:
            # Read the Retry-After header - github tells you exactly how long to wait
            retry_after = response.headers.get("Retry-After")
            retry_after = float(retry_after) if retry_after else 60.0

            raise RateLimitError(
                f"Rate limit exceeded. retry after {retry_after}",
                status_code = status,
                retry_after = retry_after,
                response_body = response.text
            )

        elif 500 <= status <= 600:
            raise ServerError(
                "Server error {status}: {api_message}",
                status_code = status,
                response_body = response.text
            )

        else:
            raise UnexpectedResponseError(
                f"Unexpected status {status}: {api_message}",
                status_code = status,
                response_body = response.text
            )

    def request(
        self,
        method: str,
        path: str,
        params: dict = None,
        json: dict = None,
        extra_headers: dict = None
    ) -> requests.Response:
        """
        Makes an HTTP request.

        Arguments:
            method: GET, POST, PATCH, DELETE
            path: endpoint path, e.g.- "/user"
            params: query string params, e.g.- {"per_page": 5}
            json: request body for post/ patch
            extra_headers: any headers you want to add for just this call

        Returns:
            Raw reaponse object, caller decides what to do with it.
            We don't call .json() here because some endpoints returs no body (204).
        """

        #Build the full url
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Merge default headers with any extra headers
        headers = {**self._get_headers(), **(extra_headers or {})}

        logger.debug(
            "Making request | method= %s | url= %s | params= %s",
            method,
            url,
            params
        )

        # Layer 1: Network Error
        # These happen before the request reaches the server
        try:
            response = self.session.request(
                method = method, 
                url = url,
                params = params,
                headers = headers,
                json = json,
                timeout = self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            # No internet, DNS failure, sever connection refused
            raise NetworkError(
                f"Connection failed to {url}: {str(e)}"
            ) from e

        except requests.exceptions.Timeout as e:
            # Server didnt respons within self.timeout seconds
            raise NetworkError(
                f"Request timed out after {self.timeout}s : {url}"
            ) from e

        except requests.exceptions.RequestException as e:
            # Catch-all for any other requests library error
            raise NetworkError(
                f"Request failed: {str(e)}"
            ) from e
        
        # layer 2: HTTP status code errors
        # request reached the server - check if it is succesful
    
        logger.debug(
            "Response received | status= %s | duration= %s",
            response.status_code,
            response.elapsed.total_seconds()
        )

        # response.ok is true for 2xx status code
        if not response.ok:
            self._handle_error_response(response)

        return response

    # Convenience wrappers
    # These just calls the self.request with methods and arguments prefilled

    def get(self, path: str, params:dict = None) -> requests.Response:
        return self.request(method = "GET", path = path, params = params )

    def post(self, path: str, json: dict = None, headers: dict = None) -> requests.Response:
        return self.request(method = "POST", path = path, json = json, extra_headers = headers)

    def patch(self, path: str, json: dict = None) -> requests.Response:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str) -> requests.Response:
        return self.request("DELETE", path)