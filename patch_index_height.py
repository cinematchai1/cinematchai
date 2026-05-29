with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    "movieEl.className = 'movie-card bg-slate-900/60 backdrop-blur-sm border border-slate-700/40 rounded-2xl p-4 flex flex-col hover:bg-slate-800/80 animate-fade-in-up text-left group';",
    "movieEl.className = 'movie-card h-full bg-slate-900/60 backdrop-blur-sm border border-slate-700/40 rounded-2xl p-4 flex flex-col hover:bg-slate-800/80 animate-fade-in-up text-left group';"
)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched index.html with h-full")
