import httpx


class AuthError(Exception):
    pass


def get_token(client_id: str, client_secret: str, email: str) -> str:
    """Exchange service app credentials + user email for an OAuth access token."""
    response = httpx.post(
        "https://oauth.yandex.ru/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": client_id,
            "client_secret": client_secret,
            "subject_token": email,
            "subject_token_type": "urn:yandex:params:oauth:token-type:email",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise AuthError(f"Token request failed ({response.status_code}): {response.text}")

    data = response.json()
    if "access_token" not in data:
        raise AuthError(f"No access_token in response: {data}")

    return data["access_token"]
