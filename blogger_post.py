import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]


def get_service():
    """Google login karta hai. Pehli baar browser khulega, baad me token.json use hoga."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("blogger", "v3", credentials=creds)


def publish_post(title: str, content_html: str, labels: list, is_draft: bool = True) -> dict:
    service = get_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html,
        "labels": labels,
    }
    return (
        service.posts()
        .insert(blogId=os.getenv("BLOG_ID"), body=body, isDraft=is_draft)
        .execute()
    )


if __name__ == "__main__":
    # Test: python blogger_post.py
    from dotenv import load_dotenv

    load_dotenv()
    res = publish_post(
        "Test Post", "<p>Ye ek test post hai.</p>", ["test"], is_draft=True
    )
    print("Done:", res.get("url") or res.get("id"))
