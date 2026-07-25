import asyncio, sys, urllib.parse, re
sys.path.insert(0, '.')

async def web_search(query):
    import httpx
    c = httpx.AsyncClient(timeout=15, verify=False)
    q = urllib.parse.quote(query)
    r = await c.get(f'https://html.duckduckgo.com/html/?q={q}', headers={'User-Agent': 'Mozilla/5.0'})
    results = re.findall(r'<a[^>]*class="result__a"[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', r.text, re.DOTALL)
    await c.aclose()
    out = []
    for i, ((link, title), snippet) in enumerate(zip(results[:10], snippets[:10])):
        t = re.sub(r'<[^>]+>', '', title).strip()[:120]
        s = re.sub(r'<[^>]+>', '', snippet).strip()[:300]
        out.append(f"{i+1}. {t}\n   {s}\n   {link}")
    return '\n\n'.join(out) if out else "No results"

async def main():
    from bot_features import youtube_search, github_search, tiktok_search
    queries = [
        ("YouTube: AI features people actually want", youtube_search('AI features people actually want 2026')),
        ("YouTube: best AI tools", youtube_search('best AI tools 2026')),
        ("YouTube: AI that changed everything", youtube_search('AI changed everything 2026')),
        ("Web: AI trends", web_search('AI trends 2026')),
        ("Web: AI agent features", web_search('AI agent features most wanted 2026')),
        ("Web: Telegram AI bot features", web_search('best Telegram AI bot features 2026')),
        ("GitHub: AI agents", github_search('AI agent tools')),
        ("GitHub: AI apps", github_search('AI application')),
        ("TikTok: AI", tiktok_search('AI')),
        ("TikTok: AI tools trending", tiktok_search('AI tools trending')),
    ]
    results = await asyncio.gather(*[q[1] for q in queries], return_exceptions=True)
    for (label, _), res in zip(queries, results):
        print(f"\n{'='*60}")
        print(f'  {label}')
        print(f"{'='*60}")
        if isinstance(res, Exception):
            print(f'  Error: {res}')
        elif res:
            safe = res.encode('ascii', errors='replace').decode('ascii')
            print(safe[:2000])
        await asyncio.sleep(0.5)

asyncio.run(main())
