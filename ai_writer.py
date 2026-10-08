import datetime
import html
import json
import os
from groq import Groq, NotFoundError, BadRequestError

# Agar .env wala model na mile to inme se jo account me available hoga wo use hoga
PREFERRED_MODELS = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]


def pick_available_model(client, wanted):
    """Account me available models dekhkar sahi model chunta hai."""
    available = [m.id for m in client.models.list().data]
    if wanted in available:
        return wanted
    for name in PREFERRED_MODELS:
        if name in available:
            print(f"Model '{wanted}' nahi mila, '{name}' use kar raha hoon.")
            return name
    chat_models = [
        m for m in available
        if "whisper" not in m and "guard" not in m and "tts" not in m
    ]
    if not chat_models:
        raise RuntimeError("Account me koi chat model available nahi hai: " + ", ".join(available))
    print(f"Model '{wanted}' nahi mila, '{chat_models[0]}' use kar raha hoon.")
    return chat_models[0]


def chat_json(system_prompt, user_prompt, max_tokens=16000):
    """Groq se JSON jawab leta hai (model fallback aur ek retry ke saath)."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    def call(model_name):
        kwargs = {}
        if "gpt-oss" in model_name:
            kwargs["reasoning_effort"] = "low"  # kam sochega, zyada likhega
        return client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs,
        )

    try:
        model_to_use = model
        try:
            completion = call(model_to_use)
        except NotFoundError:
            model_to_use = pick_available_model(client, model)
            completion = call(model_to_use)
    except BadRequestError as e:
        print("Groq JSON error, ek baar dobara try kar raha hoon:", str(e)[:120])
        completion = call(model_to_use)

    return json.loads(completion.choices[0].message.content)


# ---------- Website link ----------
def get_site_info():
    url = os.getenv("SITE_URL", "").strip()
    if not url or "YOUR-WEBSITE" in url.upper() or "APNI-WEBSITE" in url.upper():
        return "", ""
    if not url.startswith("http"):
        url = "https://" + url
    name = os.getenv("SITE_NAME", "").strip() or url
    return url, name


def site_cta_html(cta_text):
    """Post ke end me aapki website ka link wala box."""
    url, name = get_site_info()
    if not url:
        return ""
    hindi = "hindi" in os.getenv("LANGUAGE", "").lower()
    default_text = (
        "इस विषय पर और जानकारी और मदद के लिए हमारी वेबसाइट देखें।"
        if hindi
        else "For more information and help on this topic, visit our website."
    )
    text = html.escape((cta_text or default_text).strip())
    button = f"{html.escape(name)} पर जाएं »" if hindi else f"Visit {html.escape(name)} »"
    return (
        '<div style="border:2px solid #e0a800;border-radius:8px;padding:16px;'
        'margin:28px 0;background:#fff8e1;">'
        f'<p style="margin:0 0 10px 0;">{text}</p>'
        f'<p style="margin:0;"><a href="{html.escape(url)}" target="_blank" rel="noopener">'
        f"<strong>{button}</strong></a></p></div>"
    )


# ---------- Blog likhna ----------
def write_blog(research: dict) -> dict:
    """Research data se Groq ke through blog post likhwata hai."""
    language = os.getenv("LANGUAGE", "English")
    niche = os.getenv("NICHE", "general")
    site_url, site_name = get_site_info()
    site_desc = os.getenv("SITE_DESC", "").strip()

    research_text = json.dumps(research, ensure_ascii=False, indent=2)

    if site_url:
        site_rules = f"""- The blog belongs to the website "{site_name}" ({site_url}). Website description: {site_desc or 'not given'}.
- Mention {site_name} naturally ONCE in the body (for example near the conclusion) as a helpful resource,
  using an HTML link like <a href="{site_url}">{site_name}</a>.
- Do NOT claim any services, products or prices of the website beyond its description above.
- Do not add any other external links."""
        cta_key = '"cta_text": "one friendly sentence inviting readers to visit the website for more help on this topic",'
    else:
        site_rules = "- Do not add any external links."
        cta_key = ""

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
- 800 to 1200 words, friendly and clear tone, short paragraphs.
- Use HTML only: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <a>. No <h1>, no <html>/<body> tags.
- Start with a short intro. From the research, use ONLY the questions and searches that are clearly
  about the main keyword. IGNORE anything off-topic (for example food or recipes when the topic is
  houses). Turn the relevant ones into natural section headings.
- Never write the words "People Also Ask" or "PAA" anywhere in the post.
- End with a short FAQ and a conclusion.
- Do not invent statistics, prices or fake facts. Never give specific rupee amounts, cost per sq ft,
  timelines or percentages. Instead explain the factors that affect cost or time and say that real
  figures vary by city, materials and time, so readers should get local quotes.
- Write the title in the same language and script as the post (Hindi in Devanagari).
- Do not mention that you are an AI.
- The current year is {datetime.date.today().year}. Never use any other year in the title or text. Prefer not to put a year in the title at all.
{site_rules}

Return JSON with exactly these keys:
{{
  "title": "SEO friendly title under 65 characters",
  "content_html": "full post HTML",
  "labels": ["3 to 5 short labels"],
  {cta_key}
  "meta_description": "under 155 characters"
}}
"""

    post = chat_json(system_prompt, user_prompt, max_tokens=16000)

    for key in ("title", "content_html"):
        if not post.get(key):
            raise ValueError(f"AI response me '{key}' missing hai")
    post.setdefault("labels", [])
    post.setdefault("meta_description", "")

    # Website ka link box hamesha post ke end me jud jata hai
    post["content_html"] += site_cta_html(post.get("cta_text", ""))
    return post
