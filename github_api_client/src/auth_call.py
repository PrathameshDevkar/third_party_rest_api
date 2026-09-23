import token
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_token():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    else:
        return "token not found"
def build_headers(token:str) -> dict:
    """
    Builds the headers dict that github expects.
    Authorization: Bearer <token> -> authenticates you
    Accept: application/vnd.github+json -> tells githubto use v3 json format
    X-GitHub-Api-Version → pins the API version (good practice)
    """

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def get_authenticated_user(token:str)-> dict:
    """
    GET /user -> returns your profile only (not public's)
    This endpoint only works with auth ,remove auth and you will get
    http status code of 401 i.e. Unauthenticated error
    """
    base_url = os.getenv("GITHUB_BASE_URL")
    url = f"{base_url}/user"
    headers= build_headers(token)

    response = requests.get(url, headers=headers)

    print(f"Status code is: {response.status_code}")
    print(f"type of header:{type(response.headers)}")
    print(f"type of response:{type(response)}")
    print(f"Rate limit: {response.headers.get("X-RateLimit-Limit")}")
    print(f"Rate limit: {response.headers.get("X-RateLimit-Remaining")}")

    return response.json()

def get_my_repos(token:str) -> list:
    """
    GET /user/repos -> returns the repos 
    this also works with auth + repo scope
    """

    base_url = os.getenv("GITHUB_BASE_URL")
    url = f"{base_url}/user/repos"
    headers = build_headers(token)

    params = {
        "sort": "updated", #lates repos
        "per_page": 5, #first 5 repos
        "visibility": "all" #public + private
    }

    response = requests.get(url, headers = headers, params = params)

    return response.json()

if __name__ == "__main__":
    token = get_token()

    print("=" * 50)
    print("YOUR AUTHENTICATED PROFILE")
    print("=" * 50)
    me = get_authenticated_user(token)
    print(f"Name              : {me.get('name', 'Not set')}")
    print(f"Private Repos     : {me.get('total_private_repos', 0)}")
    print(f"Disk Usage        : {me.get('disk_usage', 0)} KB")

    print("\n" + "=" * 50)
    print("YOUR RECENT REPOS")
    print("=" * 50)
    repos = get_my_repos(token)
    for repo in repos:
        visibility = "🔒 Private" if repo["private"] else "🌐 Public"
        print(f"{visibility}  {repo['name']}")
        print(f"          URL      : {repo['html_url']}")
        print(f"          Language : {repo.get('language', 'N/A')}")
        print(f"          Stars    : {repo['stargazers_count']}")
        print()