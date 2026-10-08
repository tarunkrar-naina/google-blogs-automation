import os
import random

from ai_writer import chat_json
from serp_research import research_keyword


def generate_keywords(existing, count=15):
    """Keywords khatam hone par naye topics khud banata hai."""
    niche = os.getenv("NICHE", "general")
    site_desc = os.getenv("SITE_DESC", "").strip()
    seeds = [s.strip() for s in os.getenv("SEED_TOPICS", "").split(",") if s.strip()]

    # Ek seed ya purane keyword se Google ke related searches nikalo
    base = random.choice(seeds or existing or [niche])
    ideas = []
    try:
        data = research_keyword(base)
        ideas = data["related"] + data["questions"]
    except Exception as e:
        print("Related searches nahi mile:", e)

    examples = existing[-8:]
    user_prompt = f"""
Blog niche: {niche}
Website description: {site_desc or 'not given'}
Seed topic: {base}

Google related searches / questions:
{ideas}

Existing keyword examples (match this writing style and language):
{examples}

Give {count} NEW blog post keywords that real people search on Google.
Rules:
- 3 to 8 words each, written in the same style as the examples.
- Related to the niche and website, useful for readers.
- Must not repeat or closely copy any existing keyword.
Return JSON only: {{"keywords": ["...", "..."]}}
"""
    data = chat_json("You are an SEO keyword researcher. Reply with valid JSON only.",
                     user_prompt, max_tokens=4000)

    seen = {k.lower().strip() for k in existing}
    result = []
    for k in data.get("keywords", []):
        k = " ".join(str(k).split())
        if k and k.lower() not in seen:
            seen.add(k.lower())
            result.append(k)
    return result
