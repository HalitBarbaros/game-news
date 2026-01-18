import os

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0b0b0b">
    <title>Video Game News</title>
    
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="https://placehold.co/192x192/facc15/000?text=GN">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0b0b0b; --card-bg: #161616; --text: #ffffff; --accent: #facc15; --subtext: #a1a1aa; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        
        /* HEADER */
        header { 
            background: rgba(0,0,0,0.8); 
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255,255,255,0.1); 
            padding: 20px; 
            text-align: center; 
            position: sticky;
            top: 0;
            z-index: 100;
        }
        h1 { font-family: 'Oswald', sans-serif; font-size: 1.8rem; margin: 0; letter-spacing: 2px; text-transform: uppercase; }
        h1 span { color: var(--accent); }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        /* --- ANIMATED GRID --- */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 25px; 
        }
        
        /* --- INTERACTIVE CARD DESIGN --- */
        .card { 
            position: relative;
            height: 400px; 
            border-radius: 12px;
            overflow: hidden; 
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            border: 1px solid #333;
            
            /* Initial Load Animation */
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }
        
        .card.visible { opacity: 1; transform: translateY(0); }

        /* The Background Image */
        .card img { 
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            transition: transform 0.5s ease;
        }
        .card:hover img { transform: scale(1.05); }

        /* Gradient Overlay */
        .card::after {
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(to top, #000 10%, rgba(0,0,0,0.8) 50%, transparent 100%);
        }

        /* The Content Box (Title + Summary) */
        .content { 
            position: absolute; 
            bottom: 0; left: 0; width: 100%; 
            padding: 25px; box-sizing: border-box; 
            z-index: 2; 
            transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            transform: translateY(60px); /* Push summary down initially */
        }

        .card:hover .content { transform: translateY(0); }

        .meta { 
            font-size: 0.75rem; font-weight: bold; text-transform: uppercase; 
            color: var(--accent); margin-bottom: 8px; font-family: 'Oswald', sans-serif; letter-spacing: 1px;
        }
        
        h2 { 
            margin: 0 0 10px 0; font-size: 1.4rem; line-height: 1.2; 
            font-family: 'Oswald', sans-serif; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        }
        
        p { 
            font-size: 0.95rem; color: #ccc; margin: 0; line-height: 1.5;
            display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
            opacity: 0; transition: opacity 0.4s ease 0.1s;
        }
        
        .card:hover p { opacity: 1; }
        
        
        /* --- MODAL (POPUP) --- */
        #modal-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.95); z-index: 1000; overflow-y: auto;
            backdrop-filter: blur(8px);
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        #modal-content {
            max-width: 800px; margin: 40px auto; background: #111; padding: 0;
            border-radius: 16px; border: 1px solid #333; position: relative;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        
        #close-btn {
            position: absolute; top: 20px; right: 20px;
            background: rgba(0,0,0,0.5); color: white; border: 1px solid rgba(255,255,255,0.2);
            border-radius: 50%; width: 40px; height: 40px; font-size: 24px; cursor: pointer; z-index: 10;
            transition: 0.2s;
        }
        #close-btn:hover { background: var(--accent); color: #000; border-color: var(--accent); }
        
        #modal-img { width: 100%; height: 350px; object-fit: cover; border-top-left-radius: 16px; border-top-right-radius: 16px; }
        
        #modal-text-container { padding: 30px; }
        #modal-title { font-family: 'Oswald', sans-serif; font-size: 2.2rem; margin-top: 0; line-height: 1.1; }
        #modal-body { font-size: 1.1rem; line-height: 1.8; color: #d4d4d8; margin-bottom: 30px; white-space: pre-wrap; }

        #modal-link-btn {
            display: block; width: 100%; text-align: center; background: var(--accent); color: #000;
            padding: 16px; border-radius: 8px; font-weight: bold; text-decoration: none;
            text-transform: uppercase; font-family: 'Oswald', sans-serif; letter-spacing: 1px;
            transition: 0.2s;
        }
        #modal-link-btn:hover { background: #fff; transform: translateY(-2px); }

        #loading { text-align: center; color: var(--accent); margin-top: 50px; font-family: 'Oswald', sans-serif; letter-spacing: 2px; }
        
        #install-btn {
            display: none; position: fixed; bottom: 20px; left: 50%;
            transform: translateX(-50%); background: var(--accent); color: #000;
            padding: 12px 24px; border-radius: 50px; font-weight: bold;
            box-shadow: 0 4px 12px rgba(250, 204, 21, 0.4); cursor: pointer; z-index: 900;
        }
    </style>
</head>
<body>
    <header><h1>GAME <span>NEWS</span></h1></header>
    
    <div class="container">
        <div id="loading">INITIALIZING...</div>
        <div id="news-grid" class="grid"></div>
    </div>
    
    <div id="install-btn">📲 Install App</div>

    <div id="modal-overlay">
        <div id="modal-content">
            <button id="close-btn" onclick="closeModal()">&times;</button>
            <img id="modal-img" src="" alt="">
            <div id="modal-text-container">
                <h1 id="modal-title"></h1>
                <div id="modal-body"></div> 
                <a id="modal-link-btn" href="#" target="_blank">Read Full Story</a>
            </div>
        </div>
    </div>

    <script>
        let deferredPrompt;
        const installBtn = document.getElementById('install-btn');
        window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; installBtn.style.display = 'block'; });
        installBtn.addEventListener('click', () => { installBtn.style.display = 'none'; deferredPrompt.prompt(); });
        if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js');

        const feeds = [
            { name: "Wario64", url: "https://bsky.app/profile/wario64.bsky.social/rss", type: "bsky" },
            { name: "TheGameAwards", url: "https://bsky.app/profile/thegameawards.bsky.social/rss", type: "bsky" },
            { name: "Jason Schreier", url: "https://bsky.app/profile/jasonschreier.bsky.social/rss", type: "bsky" },
            { name: "Gematsu", url: "https://gematsu.com/feed", type: "std" },
            { name: "VG247", url: "https://www.vg247.com/feed", type: "std" },
            { name: "Eurogamer", url: "https://www.eurogamer.net/feed", type: "std" },
            { name: "IGN", url: "https://feeds.ign.com/ign/news", type: "std" },
            { name: "GameSpot", url: "https://www.gamespot.com/feeds/news/", type: "std" },
            { name: "Kotaku", url: "https://kotaku.com/rss", type: "std" }
        ];

        const grid = document.getElementById('news-grid');
        const loading = document.getElementById('loading');
        let allArticles = [];
        let completed = 0;

        feeds.forEach(source => {
            const proxy = 'https://api.rss2json.com/v1/api.json?rss_url=' + encodeURIComponent(source.url);
            fetch(proxy).then(r => r.json()).then(data => {
                if(data.items) {
                    data.items.slice(0, 10).forEach(item => {
                        
                        // SMART TEXT ENGINE (Safe Version)
                        let desc = item.description || "";
                        let cont = item.content || "";
                        let cleanDesc = desc.replace(/<[^>]*>?/gm, '').trim();
                        let cleanCont = cont.replace(/<[^>]*>?/gm, '').trim();
                        
                        // Pick the longest available text from the feed itself
                        let fullText = cleanCont.length > cleanDesc.length ? cleanCont : cleanDesc;
                        let gridText = fullText.length > 140 ? fullText.substring(0, 140) + "..." : fullText;

                        let img = item.enclosure?.link || item.thumbnail;
                        let hasImage = true;
                        if (!img) {
                            if (source.type === 'bsky') { hasImage = false; img = ""; } 
                            else { img = "https://placehold.co/600x400/161616/333?text=" + source.name; }
                        }

                        allArticles.push({
                            title: source.type === 'bsky' ? "Status Update" : item.title,
                            gridText: gridText,
                            fullText: fullText, 
                            link: item.link,
                            image: img,
                            hasImage: hasImage,
                            source: source.name,
                            type: source.type,
                            date: new Date(item.pubDate)
                        });
                    });
                }
            }).finally(() => {
                completed++;
                if(completed === feeds.length) {
                    allArticles.sort((a,b) => b.date - a.date);
                    loading.style.display = 'none';
                    renderGrid();
                }
            });
        });

        function renderGrid() {
            grid.innerHTML = allArticles.map((a, index) => `
                <div class="card ${a.hasImage ? '' : 'no-image'}" onclick="openModal(${index})">
                    <img src="${a.image}">
                    <div class="content">
                        <div class="meta">
                            <span class="${a.type}">
                                ${a.type === 'bsky' ? '🦋 ' + a.source : '📰 ' + a.source}
                            </span>
                            • ${timeAgo(a.date)}
                        </div>
                        ${a.type !== 'bsky' ? `<h2>${a.title}</h2>` : ''}
                        <p>${a.gridText}</p>
                    </div>
                </div>
            `).join('');

            // TRIGGER ANIMATION
            const cards = document.querySelectorAll('.card');
            cards.forEach((card, i) => {
                setTimeout(() => { card.classList.add('visible'); }, i * 100);
            });
        }

        const modal = document.getElementById('modal-overlay');
        const modalImg = document.getElementById('modal-img');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalBtn = document.getElementById('modal-link-btn');

        window.openModal = function(index) {
            const article = allArticles[index];
            modalTitle.innerText = article.title;
            if(article.title === "Status Update") modalTitle.style.display = "none";
            else modalTitle.style.display = "block";
            
            modalBtn.href = article.link;
            
            if(article.hasImage) {
                modalImg.src = article.image;
                modalImg.style.display = "block";
            } else {
                modalImg.style.display = "none";
            }

            modalBody.innerHTML = article.fullText; 
            
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
        }

        window.closeModal = function() {
            modal.style.display = "none";
            document.body.style.overflow = "auto";
        }
        modal.addEventListener('click', function(e) { if (e.target === modal) closeModal(); });

        function timeAgo(date) {
            const seconds = Math.floor((new Date() - date) / 1000);
            let interval = seconds / 3600;
            if (interval > 1) return Math.floor(interval) + "h";
            interval = seconds / 60;
            if (interval > 1) return Math.floor(interval) + "m";
            return "Now";
        }
    </script>
</body>
</html>
"""

manifest_content = """{
  "name": "Game News",
  "short_name": "GameNews",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0b0b0b",
  "theme_color": "#0b0b0b",
  "icons": [
    {
      "src": "https://placehold.co/192x192/facc15/000?text=GN",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "https://placehold.co/512x512/facc15/000?text=GN",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}"""

sw_content = """
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open('gamenews-v1').then((cache) => cache.addAll(['./', './index.html'])));
});
self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then((response) => response || fetch(e.request)));
});
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
with open("manifest.json", "w", encoding="utf-8") as f:
    f.write(manifest_content)
with open("sw.js", "w", encoding="utf-8") as f:
    f.write(sw_content)

print("✅ Stable Version Restored (Jina Removed)")
