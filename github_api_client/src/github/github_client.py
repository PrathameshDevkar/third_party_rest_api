import os
import logging 
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)

class GitHubClient(BaseAPIClient):
    """
    Github rest api client.
    
    Inherits all http api mechanics from BaseAPIClient.
    Only adds:
    - Github specific headers(auth, accept, api version)
    - Github specifi methods(get_users, get_repos etc.)
    """

    API_VERSION = "2022-11-28" 

    def __init__(self,token: str = None, timeout:int = 30):

        self.token = token or os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise EnvironmentError(
                "Github token not found."
                "Pass it directly or set it in the .env file"
            )

        base_url = os.environ.get("GITHUB_BASE_URL","https://api.github.com")

        # Call parent __init__ to set the base_url, timeout and session
        # super() refers to BaseAPIClient

        super().__init__(base_url = base_url, timeout = timeout)

        logger.info("Github client is ready | base_url = %s", self.base_url)

    def _get_headers(self) -> dict:
        """
        Overrides the _get_headers of the BaseAPIClient.
        This headers will be sent with every Github request.    
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION
        }

    # API methods
    # each method maps to one github endpoint
    # They call self.get() and self.post() from the parent class

    def get_authenticated_user(self) -> dict:
        """
        GET /user returns your own profile
        """
        response = self.get("/user")
        return response.json()

    def get_user(self, username:str) -> dict:
        "GET /users/{username} - Returns any public user"
        response = self.get(f"/users/{username}")
        return response.json()

    def get_my_repos(self, sort: str= "updated", per_page: int= 5) -> dict:
        "GET /user/repos - returns your own repositories "
        response = self.get("/user/repos",
                            params = {
                                "sort": sort,
                                "per_page": per_page,
                                "visibility": "all"
                            })
        return response.json()

    def get_repo(self, owner: str, repo:str) -> dict :
        "GET /repos/{owner}/{repo} - returns a specific repo"
        response = self.get(f"/repos/{owner}/{repo}")
        return response.json()

    def star_repo(self, owner: str, repo: str) -> None :
        """
        GET /user/starred/{owner}/{repo} - stars a specific repo

        This uses put methos which returns true if succesfull.
        This will return status code of 204, i.e. no reponse.
        204 means 'succes with nothing (No body) in return. That's why we didnt use .json() here . 
        """
        response = self.request(method= "PUT", path= f"/user/starred/{owner}/{repo}")
        if response:
            return response.status_code == 204
        else:
            return response
    




