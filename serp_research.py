import os
import requests


def research_keyword(keyword: str) -> dict:
    """SerpAPI se Google search research nikalta hai."""
    params = {
        "engine": "google",
        "q": keyword,
        "hl": os.getenv("SERP_HL", "en"),
        "gl": os.getenv("SERP_GL", "in"),
        "num": 10,
        "api_key": os.getenv("SERPAPI_KEY"),
    }
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    organic = [
        {"title": r.get("title", ""), "snippet": r.get("snippet", "")}
        for r in data.get("organic_results", [])[:8]
    ]
    questions = [q.get("question", "") for q in data.get("related_questions", [])]
    related = [r.get("query", "") for r in data.get("related_searches", [])]

    return {
        "keyword": keyword,
        "organic": organic,
        "questions": [q for q in questions if q],
        "related": [r for r in related if r],
    }
