import feedparser
from google import genai
from google.genai import types
import os
import datetime

# 1. SETUP
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# 2. CONFIGURATION (With "Fake ID" to bypass blocks)
# We use a user agent so IGN thinks we are a human on Chrome
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

rss_feeds = [
    "https://feeds.ign.com/ign/news",
    "https://www.gamespot.com/feeds/news/",
    "https://kotaku.com/rss",
]

# 3. HTML TEMPLATE
html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أخبار الألعاب - Game News</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #121212; color: #ffffff; font-family: 'Tajawal', sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #bb86fc; }}
        .card {{ background: #1e1e1e; border-radius: 12px; margin-bottom: 25px; border: 1px solid #333; overflow: hidden; }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; }}
        .card-content {{ padding: 20px; }}
        h2 {{ margin-top: 0; }}
        ul {{ padding-right: 20px; color: #ccc; }}
        a {{ display: block; text-align: center; background: #3700b3; color: white; text-decoration: none; padding: 10px; margin-top: 15px; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 أخبار الألعاب - Game News</h1>
        <div style="text-align: center; color: #888; margin-bottom: 20px;">Updated: {date}</div>
        {articles}
    </div>
</body>
</html>
"""

card_template = """
<div class="card">
    <img src="{image}" onerror="this.src='https://placehold.co/600x400/1e1e1e/FFF?text=Game+News'">
    <div class="card-content">
        <h2>{headline}</h2>
        <ul>{summary_points}</ul>
        <a href="{link}" target="_blank">قراءة المزيد</a>
    </div>
</div>
"""

def get_translation(title, summary):
    prompt = f"""
    Task: Translate video game news to Arabic.
    1. Translate headline to Arabic.
    2. Summarize content into 3 short Arabic bullet points (<li>Point</li>).
    English Title: {title}
    English Content: {summary}
    Output JSON: {{ "headline": "...", "bullets": "<li>...</li><li>...</li>" }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.parsed
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return None

def main():
    articles_html = ""
    processed_count = 0
    
    print("🚀 Starting Fetcher with Anti-Block Headers...")

    for feed_url in rss_feeds:
        try:
            # THIS IS THE FIX: Sending the headers
            feed = feedparser.parse(feed_url, request_headers=HEADERS)
            
            print(f"📥 {feed_url}: Found {len(feed.entries)} entries")
            
            for entry in feed.entries:
                if processed_count >= 8: break
                
                # Image extraction
                image_url = "https://placehold.co/600x400/1e1e1e/FFF?text=Game+News"
                if 'media_content' in entry: image_url = entry.media_content[0]['url']
                
                content = getattr(entry, 'summary', getattr(entry, 'description', ''))
                
                # Translate
                print(f"   ✨ Translating: {entry.title[:30]}...")
                trans = get_translation(entry.title, content)
                
                if trans:
                    articles_html += card_template.format(
                        image=image_url,
                        headline=trans['headline'],
                        summary_points=trans['bullets'],
                        link=entry.link
                    )
                    processed_count += 1
        except Exception as e:
            print(f"❌ Error fetching feed {feed_url}: {e}")

    # Fallback if empty
    if processed_count == 0:
        articles_html = "<h3 style='text-align:center;'>❌ No news found. The sites might be blocking access.</h3>"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    final_html = html_template.format(date=now, articles=articles_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    main()
