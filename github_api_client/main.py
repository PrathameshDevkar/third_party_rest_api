from .src.github.github_client import GitHubClient
from .src.github.exceptions import (
    APIError, 
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    NetworkError
)

def demo_success(client):
    print("="*50)
    print("Valid repo")
    print("="*50)
    repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")
    print(f"Name : {repo['name']}")
    print(f"Stars: {repo['stargazers_count']}")

def demo_not_found(client):
    print("\n" + "="*50)
    print("Repo that dosnt exist")
    print("="*50)
    try:
        repo = client.get_repo("PrathameshDevkar","test_repo")
        print(repo)
    except NotFoundError as e:
        print(f"Caught NotFoundError : {e}")
        print(f"Status code : {e.status_code}")
        print(f"Response body : {e.response_body}")

def demo_bad_token(client):
    print("\n","="*50)
    print("Bad token")
    print("="*50)
    try:
        bad_client = GitHubClient(token="demo_token")
        bad_client.get_authenticated_user()
    except AuthenticationError as e:
        print(f"Caught AuthenticationError : {e}")
        print(f"Response body : {e.response_body}")

def demo_catch_all(client):
    print("\n","="*50)
    print("Catching any API error")
    print("="*50)
    try:
        #Doenst matter what kind of error this throws
        client.get_repo("non_existant_owner", "non_existant_repo")
    except NotFoundError as e:
        print(f"Specifically a not found error: {e}")
        print(f"Response body : {e.response_body}")
    except APIError as e:
        #Fallback - catches Authenticationerror, servererror
        print(f"Some other api error: {e}")
        print(f"Response body : {e.response_body}")

def demo_rate_limit_info(client):
    print("\n","="*50)
    print("Rate limit status")
    print("="*50)
    # Make a real call and rate limit headers from response
    # We need the raw response here, not just .json()
    response = client.session.get(
        f"{client.base_url}/user",
        headers = client._get_headers()
    )
    remaining= response.headers.get("X-RateLimit-Remaining")
    limit= response.headers.get("X-RateLimit-Limit")
    reset_ts = response.headers.get("X-RateLimit-Reset")
    retry_after = response.headers.get("Retry-After")

    import datetime
    reset_time = datetime.datetime.fromtimestamp(int(reset_ts))

    print(f"  Used      : {int(limit) - int(remaining)} / {limit}")
    print(f"  Remaining : {remaining}")
    print(f"  Resets at : {reset_time.strftime('%H:%M:%S')}")

def main():
    client = GitHubClient()

    # Authenticated user
    print("="*50)
    print("Authenticated user")
    print("="*50)

    me = client.get_authenticated_user()
    print(f"Login: {me['login']}")
    print(f"Name: {me.get('name', 'not set')}")
    print(f"Repos: {me["public_repos"]}")

    # get my repos
    print("="*50)
    print("my repos")
    print("="*50)
    repos = client.get_my_repos()
    for repo in repos:
        print(f"->{repo['name']} - {'Private' if repo['private'] else 'Public'}")

    # Get specific repo
    # Authenticated user
    print("="*50)
    print("Specific repo")
    print("="*50)
    repo = client.get_repo(owner= "PrathameshDevkar", repo = "mcp_a2a_multiagent")
    print(f"Repo name: {repo['name']}")
    print(f"Description: {repo.get('description')}")


if __name__ == "__main__":
    # main()
    client = GitHubClient()

    demo_success(client)
    demo_not_found(client)
    demo_bad_token(client)
    demo_catch_all(client)
    demo_rate_limit_info(client)

