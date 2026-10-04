import json
import os
from groq import Groq


def write_blog(research: dict) -> dict:
    """Research data se Groq ke through blog post likhwata hai."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    language = os.getenv("LANGUAGE", "English")
    niche = os.getenv("NICHE", "general")

    research_text = json.dumps(research, ensure_ascii=False, indent=2)

    system_prompt = (
        "You are an expert blog writer and SEO specialist. "
        "You write original, helpful, human-sounding content. "
        "You always reply with valid JSON only."
    )

    user_prompt = f"""
Write a complete blog post for the niche: {niche}.
Main keyword: {research['keyword']}
Language: {language}

Use this Google research (top results, People Also Ask, related searches) to cover
what readers actually want. Do NOT copy any text from it.

RESEARCH:
{research_text}

Rules:
- 1000 to 1500 words, friendly and clear tone, short paragraphs.
- Use HTML only: <h2>, <h3>, <p>, <ul>, <li>, <strong>. No <h1>, no <html>/<body> tags.
- Start with a short intro, answer the People Also Ask questions in sections,
  and end with a short FAQ and a conclusion.
- Do not invent statistics, prices or fake facts. If unsure, stay general.
- Do not mention that you are an AI.

Return JSON with exactly these keys:
{{
  "title": "SEO friendly title under 65 characters",
  "content_html": "full post HTML",
  "labels": ["3 to 5 short labels"],
  "meta_description": "under 155 characters"
}}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=6000,
        response_format={"type": "json_object"},
    )

    post = json.loads(completion.choices[0].message.content)
    for key in ("title", "content_html"):
        if not post.get(key):
            raise ValueError(f"AI response me '{key}' missing hai")
    post.setdefault("labels", [])
    post.setdefault("meta_description", "")
    return post
