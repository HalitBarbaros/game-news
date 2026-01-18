import feedparser
from google import genai
from google.genai import types
import os
import datetime

# 1. SETUP
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# 2. SOURCE
rss_feeds = ["https://store.steampowered.com/feeds/news.xml"]

# 3. HTML TEMPLATE
html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game News</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #121212; color: #ffffff; font-family: 'Tajawal', sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #bb86fc; }}
        .card {{ background: #1e1e1e; border-radius: 12px; margin-bottom: 25px; border: 1px solid #333; overflow: hidden; }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; }}
        .card-content {{ padding: 20px; }}
        .tag {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-bottom: 8px; }}
        .tag.ar {{ background: #03dac6; color: #000; }} /* Arabic Success */
        .tag.en {{ background: #cf6679; color: #000; }} /* English Fallback */
        h2 {{ margin-top: 0; color: #fff; }}
        ul {{ padding-right: 20px; color: #ccc; }}
        a {{ display: block; text-align: center; background: #3700b3; color: white; text-decoration: none; padding: 10px; margin-top: 15px; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 أخبار الألعاب</h1>
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
        <span class="tag {lang_class}">{lang_text}</span>
        <h2>{headline}</h2>
        {body}
        <a href="{link}" target="_blank">Full Article</a>
    </div>
</div>
"""

def get_translation(title, summary):
    prompt = f"""
    Task: Translate video game news to Arabic.
    1. Translate headline to Arabic.
    2. Summarize content into 2 short bullet points.
    English Title: {title}
    English Content: {summary}
    Output JSON: {{ "headline": "...", "bullets": "<li>...</li><li>...</li>" }}
    """
    try:
        # Trying a standard model to be safe
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.parsed
    except:
        return None

def main():
    articles_html = ""
    
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]: # Top 5 articles
                
                # Image Logic
                image_url = "https://placehold.co/600x400/1e1e1e/FFF?text=Game+News"
                if 'media_content' in entry: image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                     for l in entry.links:
                         if l['type'].startswith('image'): image_url = l['href']; break

                content = getattr(entry, 'summary', getattr(entry, 'description', ''))
                
                # Try Translating
                trans = get_translation(entry.title, content)
                
                if trans:
                    # SUCCESS: Show Arabic
                    articles_html += card_template.format(
                        image=image_url,
                        lang_class="ar",
                        lang_text="METERGEM (Translated)",
                        headline=trans['headline'],
                        body=f"<ul>{trans['bullets']}</ul>",
                        link=entry.link
                    )
                else:
                    # FAILURE: Show English (Fallback)
                    articles_html += card_template.format(
                        image=image_url,
                        lang_class="en",
                        lang_text="English (AI Unavailable)",
                        headline=entry.title,
                        body=f"<p dir='ltr'>{content[:200]}...</p>",
                        link=entry.link
                    )
        except Exception as e:
            print(f"Feed Error: {e}")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    final_html = html_template.format(date=now, articles=articles_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    main()
