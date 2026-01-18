# THIS SCRIPT NOW JUST INSTALLS THE LIVE DASHBOARD
# The actual news fetching happens in your browser (JavaScript)
import os

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Game News</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0f172a; --card-bg: #1e293b; --text: #f1f5f9; --accent: #38bdf8; --date: #94a3b8; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        
        header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #334155; padding-bottom: 20px; }
        h1 { margin: 0; font-size: 2rem; color: #38bdf8; }
        .subtitle { color: var(--date); font-size: 0.9rem; margin-top: 5px; }
        
        #loading { text-align: center; font-size: 1.2rem; color: #fbbf24; margin-top: 50px; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; opacity: 0; transition: opacity 0.5s; }
        .grid.loaded { opacity: 1; }
        
        .card { background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid #334155; display: flex; flex-direction: column; }
        .card:hover { border-color: var(--accent); transform: translateY(-3px); transition: 0.2s; }
        
        .card img { width: 100%; height: 160px; object-fit: cover; background: #000; }
        .content { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }
        .source { color: var(--accent); font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
        h2 { font-size: 1.1rem; margin: 0 0 10px 0; line-height: 1.4; }
        p { font-size: 0.85rem; color: #cbd5e1; flex-grow: 1; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
        
        .date-tag { font-size: 0.7rem; color: #64748b; margin-top: 10px; text-align: right; }
        a { text-decoration: none; color: inherit; display: block; height: 100%; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>⚡ Live Game News</h1>
        <div class="subtitle">Updates automatically every time you refresh</div>
    </header>

    <div id="loading">Connecting to News Feeds...</div>
    <div id="news-grid" class="grid"></div>
</div>

<script>
    // 1. LIST OF FEEDS (Gematsu & VG247 are fastest for 'Twitter-like' news)
    const feeds = [
        { name: "Gematsu", url: "https://gematsu.com/feed" },
        { name: "VG247", url: "https://www.vg247.com/feed" },
        { name: "Eurogamer", url: "https://www.eurogamer.net/feed" },
        { name: "IGN", url: "https://feeds.ign.com/ign/news" },
        { name: "GameSpot", url: "https://www.gamespot.com/feeds/news/" }
    ];

    const grid = document.getElementById('news-grid');
    const loading = document.getElementById('loading');
    let allArticles = [];
    let completedFeeds = 0;

    // 2. FETCH FUNCTION (Runs in Browser)
    feeds.forEach(source => {
        // We use rss2json to bypass CORS blocks
        const proxyUrl = 'https://api.rss2json.com/v1/api.json?rss_url=' + encodeURIComponent(source.url);

        fetch(proxyUrl)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    data.items.slice(0, 4).forEach(item => { // Get top 4 from each
                        allArticles.push({
                            title: item.title,
                            link: item.link,
                            image: item.enclosure?.link || item.thumbnail || "https://placehold.co/600x400/1e293b/FFF?text=" + source.name,
                            summary: item.description.replace(/<[^>]*>?/gm, '').substring(0, 150) + "...",
                            source: source.name,
                            date: new Date(item.pubDate)
                        });
                    });
                }
            })
            .catch(err => console.log('Error fetching ' + source.name, err))
            .finally(() => {
                completedFeeds++;
                if (completedFeeds === feeds.length) {
                    renderNews();
                }
            });
    });

    function renderNews() {
        // Sort by Newest First
        allArticles.sort((a, b) => b.date - a.date);

        loading.style.display = 'none';
        grid.innerHTML = '';
        
        allArticles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <a href="${article.link}" target="_blank">
                    <img src="${article.image}" onerror="this.src='https://placehold.co/600x400/1e293b/FFF?text=News'">
                    <div class="content">
                        <div class="source">${article.source}</div>
                        <h2>${article.title}</h2>
                        <p>${article.summary}</p>
                        <div class="date-tag">${timeAgo(article.date)}</div>
                    </div>
                </a>
            `;
            grid.appendChild(card);
        });
        
        grid.classList.add('loaded');
    }

    function timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        let interval = seconds / 3600;
        if (interval > 1) return Math.floor(interval) + " hours ago";
        interval = seconds / 60;
        if (interval > 1) return Math.floor(interval) + " minutes ago";
        return "Just now";
    }
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Live Dashboard Installed.")
