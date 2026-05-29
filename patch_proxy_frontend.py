import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace 1: Autocomplete search
target_1 = "`https://v3-cinemeta.strem.io/catalog/movie/top/search=${encodeURIComponent(query)}.json`"
replacement_1 = "`/api/proxy/catalog/movie/search=${encodeURIComponent(query)}`"

if target_1 in content:
    content = content.replace(target_1, replacement_1)
    print("Success: Replaced direct autocomplete search URL.")
else:
    print("Warning: target_1 not matched.")

# Replace 2: Cinemeta catalog search in trailer fallbacks (1)
target_2 = "`https://v3-cinemeta.strem.io/catalog/${type === 'series' || type === 'tv' ? 'series' : 'movie'}/top/search=${encodeURIComponent(originalTitle || title)}.json`"
replacement_2 = "`/api/proxy/catalog/${type === 'series' || type === 'tv' ? 'series' : 'movie'}/search=${encodeURIComponent(originalTitle || title)}`"

if target_2 in content:
    content = content.replace(target_2, replacement_2)
    print("Success: Replaced direct fallback search URL (1).")
else:
    print("Warning: target_2 not matched.")

# Replace 3: Cinemeta meta fetch in trailer fallbacks (1)
target_3 = "`https://v3-cinemeta.strem.io/meta/${type === 'series' || type === 'tv' ? 'series' : 'movie'}/${imdbId}.json`"
replacement_3 = "`/api/proxy/meta/${type === 'series' || type === 'tv' ? 'series' : 'movie'}/${imdbId}`"

if target_3 in content:
    content = content.replace(target_3, replacement_3)
    print("Success: Replaced direct fallback meta URL (1).")
else:
    print("Warning: target_3 not matched.")

# Replace 4: Cinemeta catalog search in trailer fallbacks (2)
target_4 = "`https://v3-cinemeta.strem.io/catalog/${type || 'movie'}/top/search=${encodeURIComponent(originalTitle || title)}.json`"
replacement_4 = "`/api/proxy/catalog/${type || 'movie'}/search=${encodeURIComponent(originalTitle || title)}`"

if target_4 in content:
    content = content.replace(target_4, replacement_4)
    print("Success: Replaced direct fallback search URL (2).")
else:
    print("Warning: target_4 not matched.")

# Replace 5: Cinemeta meta fetch in trailer fallbacks (2)
target_5 = "`https://v3-cinemeta.strem.io/meta/${type || 'movie'}/${imdbId}.json`"
replacement_5 = "`/api/proxy/meta/${type || 'movie'}/${imdbId}`"

if target_5 in content:
    content = content.replace(target_5, replacement_5)
    print("Success: Replaced direct fallback meta URL (2).")
else:
    print("Warning: target_5 not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished frontend proxy replacements.")
