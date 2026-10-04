# Blogger Automation (SerpAPI + Groq + Blogger API)

## Setup
1. `python -m venv venv` aur activate karo (Windows: `venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `.env.example` ka naam `.env` karo aur keys bharo
4. Google Cloud Console me:
   - New project banao
   - **Blogger API v3** enable karo
   - OAuth consent screen banao (apna email Test user me add karo)
   - Credentials -> Create OAuth client ID -> **Desktop app**
   - JSON download karke `client_secret.json` naam se is folder me rakho
5. Blog ID: Blogger dashboard URL me `blogID=XXXXX` wala number
6. Test: `python blogger_post.py` (pehli baar browser me login hoga, `token.json` ban jayega)
7. Chalao: `python main.py`

## Daily auto-run (GitHub Actions)
1. Project ko **private** GitHub repo me push karo (.env, client_secret.json, token.json push nahi hote)
2. Repo -> Settings -> Secrets and variables -> Actions me ye secrets banao:
   `GROQ_API_KEY`, `SERPAPI_KEY`, `BLOG_ID`,
   `CLIENT_SECRET_JSON` (client_secret.json ka poora text),
   `TOKEN_JSON` (token.json ka poora text)
3. `.github/workflows/blog.yml` me NICHE / LANGUAGE apne hisab se change karo
4. Actions tab se "Run workflow" dabakar test karo

## Notes
- Pehle `IS_DRAFT=True` rakho, padhkar manually publish karo.
- Naye topics `keywords.txt` me ek line me ek add karo.
- Google OAuth app "Testing" mode me ho to refresh token 7 din me expire ho sakta hai.
  Isse bachne ke liye OAuth consent screen me app ko "In production" kar do.
