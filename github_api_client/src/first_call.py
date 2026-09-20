import requests

BASE_URL = "https://api.github.com"

def get_user(username: str) -> dict:
    url = f"{BASE_URL}/users/{username}"

    response = requests.get(url)

    print(f"status code: {response.status_code}")
    print(f"headers: {dict(response.headers)}")
    print(f"Body: {response.json()}")

    return response.json()

if __name__ == "__main__":
    user = get_user("PrathameshDevka")
    print("\n--- Parsed Fields ---")
    print(f"Name: {user['name']}")
    print(f"Public repos: {user['public_repos']}")
    print(f"Followers: {user['followers']}")