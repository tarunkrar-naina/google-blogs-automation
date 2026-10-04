import os
import time
from dotenv import load_dotenv

load_dotenv()

from serp_research import research_keyword
from ai_writer import write_blog
from blogger_post import publish_post

KEYWORDS_FILE = "keywords.txt"
DONE_FILE = "done_keywords.txt"


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    is_draft = os.getenv("IS_DRAFT", "True").strip().lower() == "true"
    posts_per_run = int(os.getenv("POSTS_PER_RUN", "1"))

    done = set(read_lines(DONE_FILE))
    pending = [k for k in read_lines(KEYWORDS_FILE) if k not in done]

    if not pending:
        print("Koi naya keyword nahi bacha. keywords.txt me aur add karo.")
        return

    for keyword in pending[:posts_per_run]:
        print(f"\n=== Keyword: {keyword} ===")
        try:
            print("1/3 SerpAPI research...")
            research = research_keyword(keyword)

            print("2/3 Groq se blog likh raha hoon...")
            post = write_blog(research)

            print("3/3 Blogger par bhej raha hoon...")
            result = publish_post(
                post["title"],
                post["content_html"],
                post["labels"],
                is_draft=is_draft,
            )

            with open(DONE_FILE, "a", encoding="utf-8") as f:
                f.write(keyword + "\n")

            status = "DRAFT" if is_draft else "PUBLISHED"
            print(f"[{status}] {post['title']}")
            print("Meta description (Blogger settings me daal sakte ho):", post["meta_description"])
            print("Link:", result.get("url", "(draft - Blogger dashboard me dekho)"))
        except Exception as e:
            print(f"Error ({keyword}): {e}")

        time.sleep(5)


if __name__ == "__main__":
    main()
