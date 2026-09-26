from .src.github.github_client import GitHubClient
from .src.github.exceptions import (
    APIError, 
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    NetworkError
)

# #===============================exceptiopns and status code testing=================================
# def demo_success(client:GitHubClient):
#     print("="*50)
#     print("Valid repo")
#     print("="*50)
#     repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")
#     print(f"Name : {repo.name}")
#     print(f"Stars: {repo.stargazers_count}")

# def demo_not_found(client):
#     print("\n" + "="*50)
#     print("Repo that dosnt exist")
#     print("="*50)
#     try:
#         repo = client.get_repo("PrathameshDevkar","test_repo")
#         print(repo)
#     except NotFoundError as e:
#         print(f"Caught NotFoundError : {e}")
#         print(f"Status code : {e.status_code}")
#         print(f"Response body : {e.response_body}")

# def demo_bad_token(client):
#     print("\n","="*50)
#     print("Bad token")
#     print("="*50)
#     try:
#         bad_client = GitHubClient(token="demo_token")
#         bad_client.get_authenticated_user()
#     except AuthenticationError as e:
#         print(f"Caught AuthenticationError : {e}")
#         print(f"Response body : {e.response_body}")

# def demo_catch_all(client):
#     print("\n","="*50)
#     print("Catching any API error")
#     print("="*50)
#     try:
#         #Doenst matter what kind of error this throws
#         client.get_repo("non_existant_owner", "non_existant_repo")
#     except NotFoundError as e:
#         print(f"Specifically a not found error: {e}")
#         print(f"Response body : {e.response_body}")
#     except APIError as e:
#         #Fallback - catches Authenticationerror, servererror
#         print(f"Some other api error: {e}")
#         print(f"Response body : {e.response_body}")

# def demo_rate_limit_info(client):
#     print("\n","="*50)
#     print("Rate limit status")
#     print("="*50)
#     # Make a real call and rate limit headers from response
#     # We need the raw response here, not just .json()
#     try:
#         response = client.session.get(
#             f"{client.base_url}/user",
#             headers = client._get_headers()
#         )
#         remaining= response.headers.get("X-RateLimit-Remaining")
#         limit= response.headers.get("X-RateLimit-Limit")
#         reset_ts = response.headers.get("X-RateLimit-Reset")
#         retry_after = response.headers.get("Retry-After")

#         import datetime
#         reset_time = datetime.datetime.fromtimestamp(int(reset_ts))

#         print(f"  Used      : {int(limit) - int(remaining)} / {limit}")
#         print(f"  Remaining : {remaining}")
#         print(f"  Resets at : {reset_time.strftime('%H:%M:%S')}")

    
#     except RateLimitError as e:
#         print(f"caught rate limit error: {e}")
#         print(f"Status code: {e.status_code}")
#         print(f"response body: {e.response_body}")

# def demo_network_error(client: GitHubClient):
#     print("\n"+"="*50)
#     print("Network error")
#     print("="*50)

#     try:
        
#         bad_client = GitHubClient()
#         bad_client.base_url = "https://test_site_doensnt_exist.com"

#         bad_client.get_repo(
#             "PrathameshDevkar",
#             "mcp_a2a_multiagent"
#         )
#     except NetworkError as e:
#         print(f"Caught network error: {e}")

# #=======================================================================================

# #==================================models testing=======================================
def demo_user_model(client:GitHubClient):
    print("=" * 50)
    print("USER MODEL")
    print("=" * 50)
    me = client.get_authenticated_user()

    # Attribute access — not dict key access
    # Your editor will autocomplete these
    print(f"Login        : {me.login}")
    print(f"Display Name : {me.display_name()}")   # method on the model
    print(f"Account Type : {me.account_type}")
    print(f"Member Since : {me.created_at.strftime('%B %Y')}")  # datetime object
    print(f"Public Repos : {me.public_repos}")

    # Notice: me.created_at is a real datetime object, not a string
    print(f"Type of created_at : {type(me.created_at)}")


def demo_repo_model(client):
    print("\n" + "=" * 50)
    print("REPO MODEL")
    print("=" * 50)
    repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")

    print(f"Name        : {repo.name}")
    print(f"Owner Login : {repo.owner.login}")     # nested model access
    print(f"Private     : {repo.private}")
    print(f"Created     : {repo.created_at.strftime('%d %b %Y')}")
    print(f"Active      : {repo.is_active()}")     # method on model
    print(f"Summary     : {repo.summary()}")        # method on model


def demo_language_model(client):
    print("\n" + "=" * 50)
    print("LANGUAGES MODEL")
    print("=" * 50)
    langs = client.get_repo_languages("PrathameshDevkar", "mcp_a2a_multiagent")

    print(f"Primary Language : {langs.primary_language()}")
    print(f"Total Bytes      : {langs.total_bytes():,}")
    print("Breakdown:")
    for lang, pct in langs.percentages().items():
        print(f"  {lang:<15} {pct}%")


def demo_model_safety(client:GitHubClient):
    print("\n" + "=" * 50)
    print("MODEL SAFETY — TYPO CAUGHT IMMEDIATELY")
    print("=" * 50)
    repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")

    # With raw dict: repo["naem"] → KeyError deep in your code
    # With Pydantic: repo.naem → AttributeError immediately
    # Your editor even underlines it before you run the code
    try:
        _ = repo.nam           # typo — 'naem' doesn't exist
    except AttributeError as e:
        print(f"Typo caught: {e}")

    # Optional field handled safely
    # description can be None — no KeyError, no crash
    desc = repo.description or "No description provided"
    print(f"Description : {desc}")


def demo_repo_list(client):
    print("\n" + "=" * 50)
    print("REPO LIST — TYPED OBJECTS")
    print("=" * 50)
    repos = client.get_my_repos(per_page=5)
    for repo in repos:
        # Each repo is a RepoModel — full attribute access + methods
        print(repo.summary())


# def main():
#     client = GitHubClient()

#     # Authenticated user
#     print("="*50)
#     print("Authenticated user")
#     print("="*50)

#     me = client.get_authenticated_user()
#     print(f"Login: {me['login']}")
#     print(f"Name: {me.get('name', 'not set')}")
#     print(f"Repos: {me["public_repos"]}")

#     # get my repos
#     print("="*50)
#     print("my repos")
#     print("="*50)
#     repos = client.get_my_repos()
#     for repo in repos:
#         print(f"->{repo['name']} - {'Private' if repo['private'] else 'Public'}")

#     # Get specific repo
#     # Authenticated user
#     print("="*50)
#     print("Specific repo")
#     print("="*50)
#     repo = client.get_repo(owner= "PrathameshDevkar", repo = "mcp_a2a_multiagent")
#     print(f"Repo name: {repo['name']}")
#     print(f"Description: {repo.get('description')}")


if __name__ == "__main__":
    # main()
    client = GitHubClient()

    # demo_network_error(client)
    # demo_success(client)

    # demo_not_found(client)
    # demo_bad_token(client)
    # demo_catch_all(client)
    # demo_rate_limit_info(client)

    demo_user_model(client)
    demo_repo_model(client)
    demo_language_model(client)
    demo_model_safety(client)
    demo_repo_list(client)
