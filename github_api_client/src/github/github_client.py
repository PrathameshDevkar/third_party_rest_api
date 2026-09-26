import os
import logging 
from .base_client import BaseAPIClient
from .models import GitHubUserModel, RepoModel, RepoLanguagesModel

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

    def get_authenticated_user(self) -> GitHubUserModel:
        """
        GET /user returns your own profile
        """
        response = self.get("/user")

        # model_validate() Parses the dict and validates every field
        # If any field is missing or wrong type -> Validationerror raised here
        return GitHubUserModel.model_validate(response.json())

    def get_user(self, username:str) -> GitHubUserModel:
        "GET /users/{username} - Returns any public user"
        response = self.get(f"/users/{username}")
        return GitHubUserModel.model_validate(response.json())

    def get_my_repos(self, sort: str= "updated", per_page: int= 5) -> list[RepoModel]:
        "GET /user/repos - returns your own repositories "
        response = self.get("/user/repos",
                            params = {
                                "sort": sort,
                                "per_page": per_page,
                                "visibility": "all"
                            })
        return [RepoModel.model_validate(r) for r in response.json()]

    def get_repo(self, owner: str, repo:str) -> RepoModel :
        "GET /repos/{owner}/{repo} - returns a specific repo"
        response = self.get(f"/repos/{owner}/{repo}")
        return RepoModel.model_validate(response.json())

    def get_repo_languages(self, owner: str, repo: str) -> RepoLanguagesModel:
        """Returns language breakdown as a typed RepoLanguagesModel."""
        response = self.get(f"/repos/{owner}/{repo}/languages")
        return RepoLanguagesModel.from_response(response.json())

    def star_repo(self, owner: str, repo: str) -> bool :
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
    




