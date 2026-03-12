import re
import json
import os

def clean_html_tag(text):
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def main():
    md_path = "kyoto_highschool_ig_data.md"
    html_path = "hp_research_helper.html"
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    schools = []
    for line in lines:
        if line.strip().startswith('|') and '学校名' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                name = clean_html_tag(parts[1])
                has_acct = clean_html_tag(parts[2])
                
                ig_url = ""
                if "href=" in parts[3]:
                    match = re.search(r'href="(.*?)"', parts[3])
                    if match:
                        ig_url = match.group(1)
                        
                followers = clean_html_tag(parts[4])
                posts = clean_html_tag(parts[5])
                
                schools.append({
                    "name": name,
                    "has_acct": has_acct,
                    "ig_url": ig_url,
                    "followers": followers,
                    "posts": posts
                })

    schools_json = json.dumps(schools, ensure_ascii=False)


    html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>京都府高校 HP×広報リサーチ・ヘルパー</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; }
        .glass {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body class="p-8 font-sans">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">公式HP・広報戦略 リサーチダッシュボード</h1>
        <p class="text-slate-400 mb-8">各高校の「独自ステータス」や「HP×SNS連携」の状況を調査するためのサポートツールです。</p>
        
        <div class="mb-6 flex gap-4">
            <input type="text" id="searchInput" placeholder="学校名で検索..." class="px-4 py-2 rounded-lg glass text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-64">
            <select id="filterSelect" class="px-4 py-2 rounded-lg glass text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="all">すべて表示</option>
                <option value="ig_only">IG運用あり</option>
                <option value="no_ig">IG運用なし</option>
            </select>
            <button onclick="exportData()" class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 rounded-lg text-white font-bold shadow-lg shadow-green-900/20 transition-all">📥 調査データをエクスポート (JSON)</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="schoolGrid">
            <!-- Cards will be injected here -->
        </div>
    </div>

    <script>
        const schools = __SCHOOLS_JSON__;
        const grid = document.getElementById('schoolGrid');
        const searchInput = document.getElementById('searchInput');
        const filterSelect = document.getElementById('filterSelect');

        function exportData() {
            const exportData = schools.map(s => {
                return {
                    name: s.name,
                    has_acct: s.has_acct,
                    ig_url: s.ig_url,
                    followers: s.followers,
                    posts: s.posts,
                    official_hp_url: localStorage.getItem('url_' + s.name) || '',
                    research_note: localStorage.getItem('note_' + s.name) || ''
                };
            });
            
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "hp_research_data_exported.json");
            document.body.appendChild(downloadAnchorNode); // required for firefox
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }

        function renderCards() {
            grid.innerHTML = '';
            const query = searchInput.value.toLowerCase();
            const filter = filterSelect.value;

            const filtered = schools.filter(s => {
                const matchSearch = s.name.toLowerCase().includes(query);
                const matchFilter = filter === 'all' ? true : (filter === 'ig_only' ? s.has_acct === 'あり' : s.has_acct === 'なし');
                return matchSearch && matchFilter;
            });

            filtered.forEach((school, index) => {
                const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(school.name + ' 公式ホームページ')}`;
                
                const card = document.createElement('div');
                card.className = 'glass rounded-xl p-6 relative overflow-hidden flex flex-col h-full';
                
                let igBadge = school.has_acct === 'あり' 
                    ? `<span class="px-2 py-1 bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md text-xs font-bold shadow-lg">IGあり (${school.followers}人)</span>`
                    : `<span class="px-2 py-1 bg-slate-700 rounded-md text-xs font-bold text-slate-300">IGなし</span>`;

                let igLink = school.ig_url 
                    ? `<a href="${school.ig_url}" target="_blank" class="text-pink-400 hover:text-pink-300 text-sm flex items-center gap-1 mt-3 transition-colors">▶︎ Instagramを開く</a>`
                    : '';

                let savedNote = localStorage.getItem('note_' + school.name) || '';
                let savedUrl = localStorage.getItem('url_' + school.name) || '';
                
                card.innerHTML = `
                    <div class="flex justify-between items-start mb-4">
                        <h2 class="text-xl font-bold text-white leading-tight pr-4 border-l-4 border-blue-500 pl-3">${school.name}</h2>
                        ${igBadge}
                    </div>
                    
                    <div class="flex-grow space-y-3">
                        <div>
                            <label class="text-xs text-slate-400 mb-1 block">公式HP URL</label>
                            <div class="flex gap-2">
                                <input type="text" id="url_${index}" value="${savedUrl}" class="flex-grow bg-slate-800/50 border border-slate-700 rounded-lg p-2 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all" placeholder="URLを貼り付け (自動保存)">
                                <button onclick="navigator.clipboard.readText().then(t => { document.getElementById('url_${index}').value = t; document.getElementById('url_${index}').dispatchEvent(new Event('input')) })" class="bg-slate-700 hover:bg-slate-600 px-3 rounded-lg text-xs font-semibold transition-colors" title="クリップボードから貼り付け">貼付</button>
                            </div>
                        </div>
                        <textarea id="textarea_${index}" class="w-full h-24 bg-slate-800/50 border border-slate-700 rounded-lg p-3 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all" placeholder="調査メモを記入... (自動保存されます)">${savedNote}</textarea>
                    </div>

                    <div class="flex flex-col gap-3 mt-auto pt-4 border-t border-slate-700/50">
                        <button onclick="window.open('${searchUrl}', 'searchWindow', 'width=1000,height=800')" class="bg-blue-600 hover:bg-blue-500 text-white text-center py-2 rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-blue-900/20">🔍 HPをGoogle検索 (小窓で開く)</button>
                        ${igLink}
                    </div>
                `;
                grid.appendChild(card);
                
                // Add event listeners for auto-saving
                const textarea = document.getElementById('textarea_' + index);
                textarea.addEventListener('input', (e) => {
                    localStorage.setItem('note_' + school.name, e.target.value);
                });
                
                const urlInput = document.getElementById('url_' + index);
                urlInput.addEventListener('input', (e) => {
                    localStorage.setItem('url_' + school.name, e.target.value);
                });
            });
        }

        searchInput.addEventListener('input', renderCards);
        filterSelect.addEventListener('change', renderCards);

        // Initial render
        renderCards();
    </script>
</body>
</html>
"""
    
    html_content = html_template.replace("__SCHOOLS_JSON__", schools_json)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    
    print(f"Successfully generated {html_path}")

if __name__ == "__main__":
    main()
