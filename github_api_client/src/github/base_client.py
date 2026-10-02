# from datetime import time
import time
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
    UnexpectedResponseError,
    MaxRetriesExceededError

)

import re
import random


load_dotenv()

#logging gives timestamps, severity level and can be turned off in the production
logging.basicConfig(
    level = logging.DEBUG,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

#Exceptions that are safe to retry
RETRYABLE_EXCEPTIONS = (RateLimitError, ServerError, NetworkError)

#Status code that are safe to retry
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def _calculate_backoff(attempt: int, base_delay: float, max_delay: float) -> float:
    """
    Calculates how long to wait before the next retry.

    Formula: min((base_delay * 2^attempt + jitter), max_delay)

    attempt: which attempt just failed
    base_delay: starting delay in seconds
    max_delay: cap- never wait longer than this

    jitter: random value added to the delay. Prevents multiple user retrying at the same time.


    Examples with base_delay=1.0:
    attempt 0 → min(1 * 1  + jitter, 60) → ~1-2s
    attempt 1 → min(1 * 2  + jitter, 60) → ~2-3s
    attempt 2 → min(1 * 4  + jitter, 60) → ~4-5s
    attempt 3 → min(1 * 8  + jitter, 60) → ~8-9s
    attempt 4 → min(1 * 16 + jitter, 60) → ~16-17s
    attempt 5 → min(1 * 32 + jitter, 60) → ~32-33s
    """
    jitter = random.uniform(0,1)
    delay = min(base_delay * (2**attempt) + jitter, max_delay)
    return delay

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

    def __init__(
        self, 
        base_url: str, 
        timeout: int = 30,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
        ):
        """
        base url: root url ,for example- https://api.github.com
        timeout: seconds to wait before giving up on the request    
                always set this- without this the code can 
                hang forever if the server stops responding.
        max_retries: how many times to retry a failed request
        base_delay: starting backoff delay in seconds
        max_delay: maximum wait between retries
        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.session = requests.Session()

        logging.debug(
            "BaseAPIClient initialized | base_url= %s | timeout= %s | max_retries= %s",
            self.base_url,
            self.timeout,
            self.max_retries
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

    def _should_retry(self, exception: Exception) -> bool:
        """
        Returns true if this exception is worth trying,
        otherwise false if the retry is pointless

        This is the decision gate before every retry
        """
        return isinstance(exception, RETRYABLE_EXCEPTIONS)

    def _get_wait_time(self, exception: Exception, attempt: int) -> float:
        """
        Decides how long to wait before the next retry.

        For RateLimitError: use the Retry-After header value- the server
        is telling is how long to wait.
        """
        if isinstance(exception, RateLimitError) and exception.retry_after:
            wait = exception.retry_after + random.uniform(0,1)

            logger.info(
                "Rate limit hit - Using Retry-After header | wait= %.2fs",
                wait    
            )
            return wait
        
        #ServerError or NetworkError use exponential backoff
        wait = _calculate_backoff(attempt, self.base_delay, self.max_delay)
        return wait

    def request(
        self,
        method: str,
        path: str,
        params: dict = None,
        json: dict = None,
        extra_headers: dict = None
    ) -> requests.Response:
        """
        Makes an HTTP request with automatic retry logic.

        Retry flow- 
        attempt 1 -> faild with retryable error.
            - Calculate wait time
            - Log warning with attempt numebr and wait
            - sleep (wait)
        
        attempt 2 -> fails again
            - Calculate wait time (longer this time)
            - sleep(wait)

        attempt 3 -> fails again
            - This was the last attempt
            - Raise MaxRetriesExceededError with the last exception

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

        last_exception = None

        for attempt in range(self.max_retries+1):
            is_last_attempt = attempt == self.max_retries

            try:
                logger.debug(
                    "Making request | method=%s | url=%s | params=%s | attempt=%s/%s",
                    method,
                    url,
                    params,
                    attempt+1,
                    self.max_retries+1
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
                    "Response received | status= %s | duration= %.3fs",
                    response.status_code,
                    response.elapsed.total_seconds()
                )

                # response.ok is true for 2xx status code
                if not response.ok:
                    self._handle_error_response(response)

                # Success----------------------------------
                if attempt>0:
                    logger.info(
                        "Request succeeded after %s retries | url= %s",
                        attempt,
                        url
                    )

                return response
            
            except Exception as e:
                last_exception = e

                # Non-retryable errors (400,401,403,404)
                # No point in retrying these, they wont fix themselves
                if not self._should_retry(e):
                    logger.error(
                        "Non-retryable error | type= %s | url= %s",
                        type(e).__name__,
                        url
                    )
                    raise

                # This was the last attempt- Give up
                if is_last_attempt:
                    logger.error(
                        "All %s attempts failed | url= %s | last_error= %s",
                        self.max_retries+1,
                        url,
                        e
                    )

                    raise MaxRetriesExceededError(
                     f"Request to {url} failed after {self.max_retries} attempt",
                     attempts = self.max_retries+1,
                     last_exception = e,
                     status_code = getattr(e, "status_code", None)
                    ) from e

                #calculate wait time and retry
                wait = self._get_wait_time(e, attempt)
                logger.warning(
                    "Retryable error | type= %s | attempt= %s/%s | "
                    "waiting= %.2fs | url= %s",
                    e,
                    attempt+1,
                    self.max_retries+1,
                    wait,
                    url
                )
                time.sleep(wait)


            

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

    def _parse_next_url(self, link_header: str) -> str | None:
        """
        Parses github's link header to extract the 'next' page url.

        github link header looks like this - 
        https://api.github.com/user/repos?page=2>; rel="next",
        https://api/github.com/user/repos?page=4>; rel="last

        We use regx to find the URL where rel="next"
        returns none if there is no next page
        """

        if not link_header:
            return None

        # Pattern: find <URL> followed by ; rel="next"
        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        if match:
            return match.group(1)   # the URL inside < >
        return None

    def paginate(
        self,
        path: str,
        params: dict= None,
        max_pages: int = 10
    ):
        """
        Generator that yields one page- list of items at a time.

        Why a generator instead of list:
        ---------------------------------------
        A list would fetch all pages before returning anything.
        If there are 100 pages then you would have to wait for 100 API calls.

        A generator returns one page, yield immidiately, 
        then fetches the next page ony when you ask for it.
        You can stop at any page without fetching the rest.

        max_pages: safety limit- prevents infinite loop if 
                    API has bug and never stops sending next pages

        path: API endpoint- ex. "user/repos"
        params: query params ex. {"sort":"updated","per_page":10}     
        """
        current_params = dict(params or {})
        pages_fetched=0
        next_url = None # First request uses path, the subsequent uses next_url

        while True:
            pages_fetched +=1

            if pages_fetched > max_pages:
                logger.warning(
                    "paginate() hit max_pages=%s limit on path=%s"
                    "increase the max_pages limit if you want more",
                    max_pages,
                    path
                )
                break
                
            # First page: use (path+params)
            # subsequent pages: use full next_url(it already has parmas baked in)
            if next_url is None:
                response = self.request("GET", path, params= current_params)
                logger.debug(
                    "first page repsonse- Response: %s",
                    response.json()
                )
            
            else:
                # for the next pages fetch full URL directly
                # we bypass the self.request() as the URL is already complete
                headers = self._get_headers()
                logger.debug(
                    "Fetching the next page | page=%s | URL=%s",
                    pages_fetched,
                    next_url
                )

                try:
                    response = self.session.get(
                        next_url,
                        headers = headers,
                        timeout = self.timeout
                    )

                except Exception as e:
                    raise NetworkError(f"Pagination failed: {str(e)}") from e

                if not response.ok:
                    self._handle_error_response(response)
                
            data = response.json()

            logger.debug(
                "Pages fetched= %s | items= %s | has_next=%s",
                pages_fetched,
                len(data) if isinstance(data, list) else 1,
                "yes" if self._parse_next_url(response.headers.get("Link")) else "no"
            )

            # Yield pause here and gives the page to the caller
            # Execution resumes from here when the caller asks for next page
            yield data

            # Check if there is another page
            next_url = self._parse_next_url(response.headers.get("Link"))
            if not next_url:
                logger.debug("No more pages after page %s", pages_fetched)
                break
        
