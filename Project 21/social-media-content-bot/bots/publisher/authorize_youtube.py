"""One-time setup: run this locally (it opens a browser for consent) after
placing your downloaded OAuth client secret at
bots/publisher/youtube_client_secret.json. Stores a refresh token so the
daily pipeline never needs a browser again.
"""

from youtube_client import run_authorization_flow

if __name__ == "__main__":
    run_authorization_flow()
