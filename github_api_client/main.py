from .src.github.github_client import GitHubClient
from .src.github.base_client import _calculate_backoff

from .src.github.exceptions import (
    APIError, 
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    NetworkError,
    MaxRetriesExceededError
)
from .src.github.models import RepoModel

from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
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
# def demo_user_model(client:GitHubClient):
#     print("=" * 50)
#     print("USER MODEL")
#     print("=" * 50)
#     me = client.get_authenticated_user()

#     # Attribute access — not dict key access
#     # Your editor will autocomplete these
#     print(f"Login        : {me.login}")
#     print(f"Display Name : {me.display_name()}")   # method on the model
#     print(f"Account Type : {me.account_type}")
#     print(f"Member Since : {me.created_at.strftime('%B %Y')}")  # datetime object
#     print(f"Public Repos : {me.public_repos}")

#     # Notice: me.created_at is a real datetime object, not a string
#     print(f"Type of created_at : {type(me.created_at)}")


# def demo_repo_model(client):
#     print("\n" + "=" * 50)
#     print("REPO MODEL")
#     print("=" * 50)
#     repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")

#     print(f"Name        : {repo.name}")
#     print(f"Owner Login : {repo.owner.login}")     # nested model access
#     print(f"Private     : {repo.private}")
#     print(f"Created     : {repo.created_at.strftime('%d %b %Y')}")
#     print(f"Active      : {repo.is_active()}")     # method on model
#     print(f"Summary     : {repo.summary()}")        # method on model


# def demo_language_model(client):
#     print("\n" + "=" * 50)
#     print("LANGUAGES MODEL")
#     print("=" * 50)
#     langs = client.get_repo_languages("PrathameshDevkar", "mcp_a2a_multiagent")

#     print(f"Primary Language : {langs.primary_language()}")
#     print(f"Total Bytes      : {langs.total_bytes():,}")
#     print("Breakdown:")
#     for lang, pct in langs.percentages().items():
#         print(f"  {lang:<15} {pct}%")


# def demo_model_safety(client:GitHubClient):
#     print("\n" + "=" * 50)
#     print("MODEL SAFETY — TYPO CAUGHT IMMEDIATELY")
#     print("=" * 50)
#     repo = client.get_repo("PrathameshDevkar", "mcp_a2a_multiagent")

#     # With raw dict: repo["naem"] → KeyError deep in your code
#     # With Pydantic: repo.naem → AttributeError immediately
#     # Your editor even underlines it before you run the code
#     try:
#         _ = repo.nam           # typo — 'naem' doesn't exist
#     except AttributeError as e:
#         print(f"Typo caught: {e}")

#     # Optional field handled safely
#     # description can be None — no KeyError, no crash
#     desc = repo.description or "No description provided"
#     print(f"Description : {desc}")


# def demo_repo_list(client):
#     print("\n" + "=" * 50)
#     print("REPO LIST — TYPED OBJECTS")
#     print("=" * 50)
#     repos = client.get_my_repos(per_page=5)
#     for repo in repos:
#         # Each repo is a RepoModel — full attribute access + methods
#         print(repo.summary())

#=======================================================================================

#===============================Pagination===========================================

# def demo_all_repos(client):
#     print("=" * 50)
#     print("ALL REPOS — MULTI-PAGE FETCH")
#     print("=" * 50)

#     # per_page=10 means GitHub gives 10 per page
#     # With 37 repos → 4 API calls (10+10+10+7)
#     repos = client.get_all_my_repos(per_page=10)

#     print(f"\nTotal repos fetched: {len(repos)}")
#     print("\nAll repos:")
#     for repo in repos:
#         print(f"  → {repo.name}")


# def demo_lazy_pagination(client):
#     print("\n" + "=" * 50)
#     print("LAZY PAGINATION — PROCESS AS THEY ARRIVE")
#     print("=" * 50)

#     # Generator — fetches page 1 immediately, pages 2+ only when needed
#     repo_generator = client.get_repos_lazy(per_page=10)

#     print("Processing repos one by one:")
#     count = 0
#     for repo in repo_generator:
#         count += 1
#         print(f"  [{count}] {repo.name} | active: {repo.is_active()}")


# def demo_early_exit(client):
#     print("\n" + "=" * 50)
#     print("EARLY EXIT — STOP WHEN FOUND")
#     print("=" * 50)

#     target = "rag"
#     print(f"Looking for repos containing '{target}'...")

#     found = []
#     pages_checked = 0

#     # We manually drive the generator so we can track pages
#     for page_data in client.paginate("/user/repos",
#                                       params={"per_page": 10, "visibility": "all"}):
#         pages_checked += 1

#         for item in page_data:
#             repo = RepoModel.model_validate(item)
#             if target.lower() in repo.name.lower():
#                 found.append(repo)

#         # Early exit — found enough, stop fetching more pages
#         if len(found) >= 2:
#             print(f"  Found enough results after {pages_checked} page(s). Stopping.")
#             break

#     print(f"\nMatching repos:")
#     for repo in found:
#         print(f"  → {repo.name}")


# def demo_search(client):
#     print("\n" + "=" * 50)
#     print("SEARCH ACROSS ALL REPOS")
#     print("=" * 50)

#     results = client.search_my_repos("rag", per_page=10)
#     print(f"Repos matching 'rag': {len(results)}")
#     for repo in results:
#         print(f"  → {repo.name} | {repo.summary()}")


# def demo_pagination_raw(client):
#     """
#     Shows raw pagination mechanics — what the Link header looks like.
#     """
#     print("\n" + "=" * 50)
#     print("RAW PAGINATION — SEE THE LINK HEADER")
#     print("=" * 50)

#     # Make a direct call so we can inspect the Link header
#     response = client.session.get(
#         f"{client.base_url}/user/repos",
#         headers=client._get_headers(),
#         params={"per_page": 5, "visibility": "all"},
#         timeout=client.timeout,
#     )

#     link_header = response.headers.get("Link", "No Link header")
#     print(f"Link Header:\n  {link_header}")
#     print(f"\nItems on this page : {len(response.json())}")

#     next_url = client._parse_next_url(link_header)
#     print(f"Next page URL      : {next_url}")


#=======================================================================================

#===============================retry-logic==================================

def demo_normal_request(client):
    """Normal request — no retries needed."""
    print("=" * 50)
    print("NORMAL REQUEST (no retry needed)")
    print("=" * 50)
    me = client.get_authenticated_user()
    print(f"Success: {me.login}")


def demo_retry_on_server_error(client):
    """
    Simulate GitHub returning 500 twice, then 200 on third attempt.
    We mock the session so we don't need a real failing server.

    mock_responses list: first two calls return 500, third returns real response.
    """
    print("\n" + "=" * 50)
    print("RETRY ON 500 SERVER ERROR")
    print("=" * 50)

    # Create fake 500 response
    fake_500 = MagicMock()
    fake_500.ok = False
    fake_500.status_code = 500
    fake_500.text = "Internal Server Error"
    fake_500.json.return_value = {"message": "Internal Server Error"}
    fake_500.elapsed.total_seconds.return_value = 0.1
    fake_500.headers = {}

    # Create fake 200 response
    fake_200 = MagicMock()
    fake_200.ok = True
    fake_200.status_code = 200
    fake_200.elapsed.total_seconds.return_value = 0.3
    fake_200.json.return_value = {
        "login": "PrathameshDevkar",
        "id": 138797139,
        "url": "https://api.github.com/users/PrathameshDevkar",
        "html_url": "https://github.com/PrathameshDevkar",
        "public_repos": 37,
        "followers": 1,
        "following": 0,
        "created_at": "2023-07-06T14:34:11Z",
        "type": "User",
    }

    # Patch session.request:
    # call 1 → 500, call 2 → 500, call 3 → 200
    with patch.object(
        client.session,
        "request",
        side_effect=[fake_500, fake_500, fake_200]
    ):
        # Speed up test — don't actually sleep for real backoff time
        with patch("time.sleep") as mock_sleep:
            try:
                user = client.get_authenticated_user()
                print(f"Eventually succeeded: {user.login}")
                print(f"Slept {mock_sleep.call_count} time(s) during retries")
                for i, call in enumerate(mock_sleep.call_args_list):
                    print(f"  Wait {i+1}: {call.args[0]:.2f}s")
            except MaxRetriesExceededError as e:
                print(f"Failed after all retries: {e}")


def demo_retry_on_rate_limit(client):
    """
    Simulate a 429 with Retry-After: 5 header.
    Client should wait exactly 5s (+ jitter) before retrying.
    """
    print("\n" + "=" * 50)
    print("RETRY ON 429 RATE LIMIT")
    print("=" * 50)

    fake_429 = MagicMock()
    fake_429.ok = False
    fake_429.status_code = 429
    fake_429.text = "rate limit exceeded"
    fake_429.json.return_value = {"message": "API rate limit exceeded"}
    fake_429.elapsed.total_seconds.return_value = 0.1
    # Retry-After header — tells client to wait 5 seconds
    fake_429.headers = {"Retry-After": "5"}

    fake_200 = MagicMock()
    fake_200.ok = True
    fake_200.status_code = 200
    fake_200.elapsed.total_seconds.return_value = 0.2
    fake_200.json.return_value = {
        "login": "PrathameshDevkar",
        "id": 138797139,
        "url": "https://api.github.com/users/PrathameshDevkar",
        "html_url": "https://github.com/PrathameshDevkar",
        "public_repos": 37,
        "followers": 1,
        "following": 0,
        "created_at": "2023-07-06T14:34:11Z",
        "type": "User",
    }

    with patch.object(
        client.session,
        "request",
        side_effect=[fake_429, fake_200]
    ):
        with patch("time.sleep") as mock_sleep:
            user = client.get_authenticated_user()
            wait_time = mock_sleep.call_args_list[0].args[0]
            print(f"Got rate limited → waited {wait_time:.2f}s (Retry-After=5 + jitter)")
            print(f"Then succeeded   → {user.login}")


def demo_max_retries_exceeded(client):
    """
    Simulate server failing all 4 attempts (initial + 3 retries).
    Should raise MaxRetriesExceededError.
    """
    print("\n" + "=" * 50)
    print("MAX RETRIES EXCEEDED")
    print("=" * 50)

    fake_500 = MagicMock()
    fake_500.ok = False
    fake_500.status_code = 500
    fake_500.text = "Internal Server Error"
    fake_500.json.return_value = {"message": "Internal Server Error"}
    fake_500.elapsed.total_seconds.return_value = 0.1
    fake_500.headers = {}

    # All 4 attempts (1 initial + 3 retries) return 500
    with patch.object(
        client.session,
        "request",
        side_effect=[fake_500, fake_500, fake_500, fake_500]
    ):
        with patch("time.sleep"):
            try:
                client.get_authenticated_user()
            except MaxRetriesExceededError as e:
                print(f"Gave up after {e.attempts} attempts")
                print(f"Last error type : {type(e.last_exception).__name__}")
                print(f"Last error      : {e.last_exception}")


def demo_no_retry_on_404(client):
    """
    404 should NOT be retried — it fails immediately.
    Retrying a 404 is pointless (resource won't appear).
    """
    print("\n" + "=" * 50)
    print("NO RETRY ON 404 (fail fast)")
    print("=" * 50)

    fake_404 = MagicMock()
    fake_404.ok = False
    fake_404.status_code = 404
    fake_404.text = "Not Found"
    fake_404.json.return_value = {"message": "Not Found"}
    fake_404.elapsed.total_seconds.return_value = 0.1
    fake_404.headers = {}

    call_count = 0

    def counting_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return fake_404

    with patch.object(client.session, "request", side_effect=counting_request):
        try:
            client.get_repo("nobody", "nothing")
        except NotFoundError as e:
            print(f"Failed immediately with NotFoundError: {e}")
            print(f"API was called exactly {call_count} time(s) — no retries wasted")


def demo_backoff_calculation():
    """
    Shows backoff values without making any real API calls.
    Pure math demonstration.
    """
    print("\n" + "=" * 50)
    print("BACKOFF CALCULATION PREVIEW")
    print("=" * 50)

    print("Exponential backoff wait times (base_delay=1.0, max_delay=60):")
    print("(jitter varies — shown as a range)")
    for attempt in range(6):
        # Show range by calculating a few times
        samples = [_calculate_backoff(attempt, 1.0, 60.0) for _ in range(5)]
        min_wait = min(samples)
        max_wait = max(samples)
        print(f"  Attempt {attempt + 1}: {min_wait:.2f}s – {max_wait:.2f}s")

#=======================================================================================

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

    # demo_user_model(client)
    # demo_repo_model(client)
    # demo_language_model(client)
    # demo_model_safety(client)
    # demo_repo_list(client)

    # demo_pagination_raw(client)
    # demo_all_repos(client)
    # demo_lazy_pagination(client)
    # demo_early_exit(client)
    # demo_search(client)

    demo_normal_request(client)
    demo_backoff_calculation()
    demo_retry_on_server_error(client)
    demo_retry_on_rate_limit(client)
    demo_max_retries_exceeded(client)
    demo_no_retry_on_404(client)