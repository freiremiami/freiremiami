"""One-time setup: run this locally, follow the printed URL, paste back the
redirected code. Stores a refresh token so the daily pipeline never needs a
browser again. Requires TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET in the env,
and your app's registered redirect URI (Content Posting API -> App details).
"""

import json
import os
import sys
from pathlib import Path

from tiktok_client import exchange_code_for_token

TOKEN_FILE = Path(__file__).parent / ".tiktok_token.json"


def main(redirect_uri: str) -> None:
    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={client_key}"
        "&scope=video.publish,video.upload"
        "&response_type=code"
        f"&redirect_uri={redirect_uri}"
        "&state=setup"
    )
    print(f"1. Open this URL and approve access:\n{auth_url}\n")
    auth_code = input("2. Paste the 'code' query param from the redirect URL: ").strip()

    token_data = exchange_code_for_token(auth_code, redirect_uri)
    TOKEN_FILE.write_text(json.dumps(token_data))
    print(f"Saved token to {TOKEN_FILE}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python authorize_tiktok.py <redirect_uri>")
        sys.exit(1)
    main(sys.argv[1])
