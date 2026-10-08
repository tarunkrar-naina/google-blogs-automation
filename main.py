import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

from serp_research import research_keyword
from ai_writer import write_blog
from blogger_post import publish_post
from keyword_generator import generate_keywords

KEYWORDS_FILE = "keywords.txt"
DONE_FILE = "done_keywords.txt"


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def append_lines(path, lines):
    text = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
    prefix = "" if (not text or text.endswith("\n")) else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(prefix + "\n".join(lines) + "\n")


def get_pending():
    done = {k.lower() for k in read_lines(DONE_FILE)}
    return [k for k in read_lines(KEYWORDS_FILE) if k.lower() not in done]


def main():
    is_draft = os.getenv("IS_DRAFT", "True").strip().lower() == "true"
    posts_per_run = int(os.getenv("POSTS_PER_RUN", "1"))

    pending = get_pending()

    # Keywords kam hon to naye khud bana lo
    if len(pending) < posts_per_run:
        print("Keywords kam hain, naye keywords bana raha hoon...")
        try:
            existing = read_lines(KEYWORDS_FILE) + read_lines(DONE_FILE)
            new_keywords = generate_keywords(existing)
            if new_keywords:
                append_lines(KEYWORDS_FILE, new_keywords)
                print(f"{len(new_keywords)} naye keywords jude.")
        except Exception as e:
            print("Naye keywords nahi ban paaye:", e)
        pending = get_pending()

    if not pending:
        print("Koi keyword nahi mila. SEED_TOPICS ya keywords.txt check karo.")
        sys.exit(1)

    failed = 0
    for keyword in pending[:posts_per_run]:
        print(f"\n=== Keyword: {keyword} ===")
        try:
            print("1/3 SerpAPI research...")
            research = research_keyword(keyword)

            print("2/3 Groq se blog likh raha hoon...")
            post = write_blog(research)

            print("3/3 Blogger par bhej raha hoon...")
            result = publish_post(
                post["title"], post["content_html"], post["labels"], is_draft=is_draft
            )

            append_lines(DONE_FILE, [keyword])

            status = "DRAFT" if is_draft else "PUBLISHED"
            print(f"[{status}] {post['title']}")
            print("Link:", result.get("url", "(draft - Blogger dashboard me dekho)"))
        except Exception as e:
            failed += 1
            print(f"Error ({keyword}): {e}")

        time.sleep(5)

    if failed:
        sys.exit(1)  # GitHub Actions me fail dikhe aur email aaye


if __name__ == "__main__":
    main()
