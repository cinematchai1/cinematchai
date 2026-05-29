import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update loadTrending function in index.html to render rich buttons with dataset attributes
target_loadtrending = '''        async function loadTrending() {
            const container = document.getElementById('trending-container');
            if (!container) return;
            container.innerHTML = `<span class="text-xs text-slate-500 animate-pulse">...</span>`;
            try {
                const res = await fetch('/api/trending');
                const data = await res.json();
                if (data.success && Array.isArray(data.trending) && data.trending.length > 0) {
                    container.innerHTML = data.trending.map(title => {
                        const escapedTitle = title.replace(/'/g, "\\\\'");
                        return `<button onclick="document.getElementById('movie-input').value='${escapedTitle}'; document.getElementById('search-form').dispatchEvent(new Event('submit'))" class="px-3 py-1 rounded-full bg-slate-800/40 hover:bg-slate-700/80 text-slate-300 transition-colors border border-slate-700/50 text-xs">${title}</button>`;
                    }).join('');
                } else {
                    throw new Error("Invalid trending data");
                }
            } catch (e) {
                console.warn("Failed to load trending, using default fallback:", e);
                const fallbacks = currentLang === 'pt'
                    ? ["A Origem", "Breaking Bad", "Interstellar", "A Guerra dos Tronos", "Matrix", "Stranger Things"]
                    : ["Inception", "Breaking Bad", "Interstellar", "Game of Thrones", "The Matrix", "Stranger Things"];
                container.innerHTML = fallbacks.map(title => {
                    const escapedTitle = title.replace(/'/g, "\\\\'");
                    return `<button onclick="document.getElementById('movie-input').value='${escapedTitle}'; document.getElementById('search-form').dispatchEvent(new Event('submit'))" class="px-3 py-1 rounded-full bg-slate-800/40 hover:bg-slate-700/80 text-slate-300 transition-colors border border-slate-700/50 text-xs">${title}</button>`;
                }).join('');
            }
        }'''

# Replace backslashes escaping carefully
replacement_loadtrending = '''        async function loadTrending() {
            const container = document.getElementById('trending-container');
            if (!container) return;
            container.innerHTML = `<span class="text-xs text-slate-500 animate-pulse">...</span>`;
            try {
                const res = await fetch('/api/trending');
                const data = await res.json();
                if (data.success && Array.isArray(data.trending) && data.trending.length > 0) {
                    container.innerHTML = data.trending.map(item => {
                        const escapedName = item.name.replace(/'/g, "\\\\'");
                        const escapedId = item.imdbId ? item.imdbId.replace(/'/g, "\\\\'") : '';
                        const escapedType = item.type ? item.type.replace(/'/g, "\\\\'") : '';
                        return `<button onclick="const input = document.getElementById('movie-input'); input.value='${escapedName}'; input.dataset.imdbId='${escapedId}'; input.dataset.contentType='${escapedType}'; input.dataset.lastTitle='${escapedName}'; document.getElementById('search-form').dispatchEvent(new Event('submit'))" class="px-3 py-1 rounded-full bg-slate-800/40 hover:bg-slate-700/80 text-slate-300 transition-colors border border-slate-700/50 text-xs">${item.name}</button>`;
                    }).join('');
                } else {
                    throw new Error("Invalid trending data");
                }
            } catch (e) {
                console.warn("Failed to load trending, using default fallback:", e);
                const fallbacks = currentLang === 'pt'
                    ? [
                        { name: "A Origem", imdbId: "tt1375666", type: "movie" },
                        { name: "Breaking Bad", imdbId: "tt0903747", type: "series" },
                        { name: "Interstellar", imdbId: "tt0816692", type: "movie" },
                        { name: "A Guerra dos Tronos", imdbId: "tt0944947", type: "series" },
                        { name: "Matrix", imdbId: "tt0133093", type: "movie" },
                        { name: "Stranger Things", imdbId: "tt5027774", type: "series" }
                      ]
                    : [
                        { name: "Inception", imdbId: "tt1375666", type: "movie" },
                        { name: "Breaking Bad", imdbId: "tt0903747", type: "series" },
                        { name: "Interstellar", imdbId: "tt0816692", type: "movie" },
                        { name: "Game of Thrones", imdbId: "tt0944947", type: "series" },
                        { name: "The Matrix", imdbId: "tt0133093", type: "movie" },
                        { name: "Stranger Things", imdbId: "tt5027774", type: "series" }
                      ];
                container.innerHTML = fallbacks.map(item => {
                    const escapedName = item.name.replace(/'/g, "\\\\'");
                    const escapedId = item.imdbId ? item.imdbId.replace(/'/g, "\\\\'") : '';
                    const escapedType = item.type ? item.type.replace(/'/g, "\\\\'") : '';
                    return `<button onclick="const input = document.getElementById('movie-input'); input.value='${escapedName}'; input.dataset.imdbId='${escapedId}'; input.dataset.contentType='${escapedType}'; input.dataset.lastTitle='${escapedName}'; document.getElementById('search-form').dispatchEvent(new Event('submit'))" class="px-3 py-1 rounded-full bg-slate-800/40 hover:bg-slate-700/80 text-slate-300 transition-colors border border-slate-700/50 text-xs">${item.name}</button>`;
                }).join('');
            }
        }'''

# Check if target matches with single or double escaped slashes
if target_loadtrending in content:
    content = content.replace(target_loadtrending, replacement_loadtrending)
    print("Success: Patched loadTrending in index.html.")
else:
    # Try with single escaped backslashes (python sometimes escapes differently)
    target_loadtrending_alt = target_loadtrending.replace("\\\\'", "\\'")
    replacement_loadtrending_alt = replacement_loadtrending.replace("\\\\'", "\\'")
    if target_loadtrending_alt in content:
        content = content.replace(target_loadtrending_alt, replacement_loadtrending_alt)
        print("Success: Patched loadTrending using alternate escaping.")
    else:
        print("Warning: loadTrending target in index.html not matched.")

# 2. Update performSearch to extract datasets and pass them to payload
target_performsearch = '''            const movie = movieInput.value.trim() || lastSearchedMovie;
            if(!movie) return;
            
            if (!isPopStateAction) {'''

replacement_performsearch = '''            const movie = movieInput.value.trim() || lastSearchedMovie;
            if(!movie) return;

            let imdbId = '';
            let trendingType = '';
            if (movieInput.dataset.lastTitle === movie) {
                imdbId = movieInput.dataset.imdbId || '';
                trendingType = movieInput.dataset.contentType || '';
            } else {
                delete movieInput.dataset.imdbId;
                delete movieInput.dataset.contentType;
                delete movieInput.dataset.lastTitle;
            }
            
            if (!isPopStateAction) {'''

if target_performsearch in content:
    content = content.replace(target_performsearch, replacement_performsearch)
    print("Success: Patched performSearch metadata extraction.")
else:
    print("Warning: target_performsearch not matched.")

# 3. Update cacheKey in performSearch to include imdbId
target_cachekey = '''            const cacheKey = `cinematch_cache_${movie.toLowerCase()}_${currentLang}_y:${afterYear}_r:${minRating}_e:${excludeGenres.toLowerCase().trim()}_t:${defaultType}_s:${surpriseMe}`;'''
replacement_cachekey = '''            const cacheKey = `cinematch_cache_${movie.toLowerCase()}_${currentLang}_y:${afterYear}_r:${minRating}_e:${excludeGenres.toLowerCase().trim()}_t:${defaultType}_s:${surpriseMe}${imdbId ? '_id:' + imdbId : ''}`;'''

if target_cachekey in content:
    content = content.replace(target_cachekey, replacement_cachekey)
    print("Success: Patched cacheKey construction in performSearch.")
else:
    print("Warning: target_cachekey not matched.")

# 4. Update payload inside performSearch to include imdbId and type
target_payload = '''                const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        defaultType,
                        surpriseMe,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData && lastMovieData.recommendations ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };'''

replacement_payload = '''                const payload = { 
                        movie, 
                        imdbId,
                        type: trendingType,
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        defaultType,
                        surpriseMe,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData && lastMovieData.recommendations ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };'''

if target_payload in content:
    content = content.replace(target_payload, replacement_payload)
    print("Success: Patched payload configuration in performSearch.")
else:
    print("Warning: target_payload not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished frontend patches.")
