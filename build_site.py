import feedparser
import datetime
import os

# 1. SOURCES
# We can add as many as we want now because we aren't limited by AI costs!
rss_feeds = [
    "https://feeds.ign.com/ign/news",
    "https://www.eurogamer.net/feed",
    "https://www.gamespot.com/feeds/news/",
    "https://www.pcgamer.com/rss",
    "https://kotaku.com/rss",
    "https://www.polygon.com/rss/index.xml"
]

# 2. CONFIGURATION
# Fake ID to prevent websites from blocking us
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# 3. HTML TEMPLATE (Modern Dark Mode)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Game News</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #0f172a; --card-bg: #1e293b; --text: #f1f5f9; --accent: #38bdf8; --date: #94a3b8; }}
        body {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        
        header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #334155; }}
        h1 {{ margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .timestamp {{ color: var(--date); font-size: 0.9rem; margin-top: 10px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        
        .card {{ background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid #334155; transition: transform 0.2s; display: flex; flex-direction: column; }}
        .card:hover {{ transform: translateY(-5px); border-color: var(--accent); }}
        
        .card img {{ width: 100%; height: 160px; object-fit: cover; background: #000; }}
        
        .content {{ padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }}
        .source-tag {{ display: inline-block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: var(--accent); margin-bottom: 8px; font-weight: bold; }}
        
        h2 {{ margin: 0 0 10px 0; font-size: 1.1rem; line-height: 1.4; }}
        p {{ font-size: 0.9rem; color: #cbd5e1; line-height: 1.5; flex-grow: 1; margin-bottom: 20px; }}
        
        a.btn {{ display: block; text-align: center; background: var(--accent); color: #0f172a; text-decoration: none; padding: 10px; border-radius: 6px; font-weight: bold; margin-top: auto; }}
        a.btn:hover {{ background: #7dd3fc; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Global Game News</h1>
            <div class="timestamp">Last Updated: {date}</div>
        </header>
        
        <div class="grid">
            {articles}
        </div>
    </div>
</body>
</html>
"""

card_template = """
<div class="card">
    <img src="{image}" onerror="this.src='https://placehold.co/600x400/1e293b/FFF?text=Game+News'">
    <div class="content">
        <span class="source-tag">{source}</span>
        <h2>{title}</h2>
        <p>{summary}</p>
        <a href="{link}" class="btn" target="_blank">Read More</a>
    </div>
</div>
"""

def clean_summary(html_summary):
    """Simple cleaner to remove HTML tags from summary"""
    from re import sub
    # Remove HTML tags
    text = sub('<[^<]+?>', '', html_summary)
    # Truncate
    return text[:150] + "..." if len(text) > 150 else text

def main():
    articles_html = ""
    total_articles = 0
    
    print("🚀 Starting Multi-Source Fetcher...")

    for feed_url in rss_feeds:
        try:
            # Determine Source Name from URL (e.g., 'ign', 'gamespot')
            source_name = "News"
            if "ign" in feed_url: source_name = "IGN"
            elif "eurogamer" in feed_url: source_name = "Eurogamer"
            elif "gamespot" in feed_url: source_name = "GameSpot"
            elif "pcgamer" in feed_url: source_name = "PC Gamer"
            elif "kotaku" in feed_url: source_name = "Kotaku"
            elif "polygon" in feed_url: source_name = "Polygon"

            print(f"📥 Fetching: {source_name}...")
            
            # Request with headers to avoid blocks
            feed = feedparser.parse(feed_url, request_headers=HEADERS)
            
            # Get top 4 stories from each site
            for entry in feed.entries[:4]:
                
                # Try to find an image
                image_url = "https://placehold.co/600x400/1e293b/FFF?text=" + source_name
                if 'media_content' in entry: 
                    image_url = entry.media_content[0]['url']
                elif 'media_thumbnail' in entry:
                    image_url = entry.media_thumbnail[0]['url']
                elif 'links' in entry:
                    for l in entry.links:
                        if l['type'].startswith('image'): image_url = l['href']; break
                
                # Clean up summary
                raw_summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                clean_text = clean_summary(raw_summary)

                articles_html += card_template.format(
                    image=image_url,
                    source=source_name,
                    title=entry.title,
                    summary=clean_text,
                    link=entry.link
                )
                total_articles += 1
                
        except Exception as e:
            print(f"⚠️ Error fetching {feed_url}: {e}")

    # Generate Final HTML
    now = datetime.datetime.now().strftime("%B %d, %H:%M UTC")
    final_html = html_template.format(date=now, articles=articles_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"✅ Success! Generated {total_articles} articles from multiple sources.")

if __name__ == "__main__":
    main()
