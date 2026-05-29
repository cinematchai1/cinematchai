import re

# 1. Update server.js
with open('server.js', 'r', encoding='utf-8') as f:
    server_js = f.read()

# Fix SQL Select
server_js = server_js.replace(
    "await pool.query('SELECT tmdb_data, omdb_data, cinemeta_data FROM movies_cache WHERE imdb_id = $1', [id]);",
    "await pool.query('SELECT tmdb_data, omdb_data, cinemeta_data FROM movies_cache WHERE imdb_id = $1 AND language = $2', [id, lang]);"
)

# Fix SQL Insert
server_js = server_js.replace(
    """INSERT INTO movies_cache (imdb_id, title, type, tmdb_data, omdb_data, cinemeta_data)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (imdb_id) DO UPDATE SET""",
    """INSERT INTO movies_cache (imdb_id, language, title, type, tmdb_data, omdb_data, cinemeta_data)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (imdb_id, language) DO UPDATE SET"""
)
server_js = server_js.replace(
    "`, [id, fallbackTitle, cleanType, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(finalData.cinemeta)]);",
    "`, [id, lang, fallbackTitle, cleanType, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(finalData.cinemeta)]);"
)

# Fix Pre-Warming Check
server_js = server_js.replace(
    "await pool.query('SELECT 1 FROM movies_cache WHERE imdb_id = $1', [id]);",
    "await pool.query('SELECT 1 FROM movies_cache WHERE imdb_id = $1 AND language = $2', [id, 'en']);"
)

# Fix Pre-Warming Insert
server_js = server_js.replace(
    """INSERT INTO movies_cache (imdb_id, title, type, tmdb_data, omdb_data, cinemeta_data)
                        VALUES ($1, $2, 'movie', $3, $4, $5)""",
    """INSERT INTO movies_cache (imdb_id, language, title, type, tmdb_data, omdb_data, cinemeta_data)
                        VALUES ($1, 'en', $2, 'movie', $3, $4, $5)"""
)
server_js = server_js.replace(
    "`, [id, fallbackTitle, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(cinemeta)]);",
    "`, [id, fallbackTitle, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(cinemeta)]);"
)

# Fix TMDB URL to include credits
server_js = server_js.replace("append_to_response=videos,translations", "append_to_response=videos,translations,credits")

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(server_js)

# 2. Update index.html
with open('public/index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

# Fix Cast visibility
index_html = index_html.replace('class="hidden md:flex flex-col gap-6 w-64 shrink-0', 'class="flex flex-col gap-6 w-full md:w-64 shrink-0')

# Fix Badges tooltips
index_html = index_html.replace('class="flex items-center gap-1 bg-rose-500/20 px-2 py-1', 'title="Rotten Tomatoes" class="flex items-center gap-1 bg-rose-500/20 px-2 py-1')
index_html = index_html.replace('class="flex items-center gap-1 bg-green-500/20 px-2 py-1', 'title="Metacritic" class="flex items-center gap-1 bg-green-500/20 px-2 py-1')
index_html = index_html.replace('class="flex items-center gap-1 bg-amber-500/20 px-2 py-1', 'title="IMDb Rating" class="flex items-center gap-1 bg-amber-500/20 px-2 py-1')

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Patch applied to local files")
