import io
import re

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update /api/trending to return full objects and handle deduplication properly
target_trending_api = '''        const fetchTop = (type) => {
            return new Promise((resolve) => {
                const url = `https://cinemeta-catalogs.strem.io/top/catalog/${type}/top.json`;
                const reqHttps = https.get(url, (resHttps) => {
                    let body = '';
                    resHttps.on('data', chunk => body += chunk);
                    resHttps.on('end', () => {
                        try {
                            const data = JSON.parse(body);
                            if (data && data.metas && Array.isArray(data.metas)) {
                                resolve(data.metas.slice(0, 10).map(m => m.name));
                            } else {
                                resolve([]);
                            }
                        } catch (e) {
                            resolve([]);
                        }
                    });
                });
                reqHttps.on('error', () => resolve([]));
                reqHttps.setTimeout(2500, () => {
                    reqHttps.abort();
                    resolve([]);
                });
            });
        };

        const [movies, series] = await Promise.all([fetchTop('movie'), fetchTop('series')]);
        
        let merged = [];
        const maxLen = Math.max(movies.length, series.length);
        for (let i = 0; i < maxLen; i++) {
            if (movies[i]) merged.push(movies[i]);
            if (series[i]) merged.push(series[i]);
        }
        
        merged = [...new Set(merged)].slice(0, 8);
        
        let isSuccess = true;
        if (merged.length === 0) {
            merged = ["Inception", "Breaking Bad", "Interstellar", "Game of Thrones", "The Matrix", "Stranger Things"];
            isSuccess = false; // Do not cache long if we got an empty result
        }
        
        if (isSuccess) {
            trendingCache = merged;
            trendingCacheTime = now;
        }
        
        res.json({ success: true, trending: merged });'''

replacement_trending_api = '''        const fetchTop = (type) => {
            return new Promise((resolve) => {
                const url = `https://cinemeta-catalogs.strem.io/top/catalog/${type}/top.json`;
                const reqHttps = https.get(url, (resHttps) => {
                    let body = '';
                    resHttps.on('data', chunk => body += chunk);
                    resHttps.on('end', () => {
                        try {
                            const data = JSON.parse(body);
                            if (data && data.metas && Array.isArray(data.metas)) {
                                resolve(data.metas.slice(0, 10).map(m => ({
                                    name: m.name,
                                    year: m.releaseInfo || m.year || '',
                                    type: m.type || type,
                                    imdbId: m.id || m.imdb_id || ''
                                })));
                            } else {
                                resolve([]);
                            }
                        } catch (e) {
                            resolve([]);
                        }
                    });
                });
                reqHttps.on('error', () => resolve([]));
                reqHttps.setTimeout(2500, () => {
                    reqHttps.abort();
                    resolve([]);
                });
            });
        };

        const [movies, series] = await Promise.all([fetchTop('movie'), fetchTop('series')]);
        
        let merged = [];
        const maxLen = Math.max(movies.length, series.length);
        for (let i = 0; i < maxLen; i++) {
            if (movies[i]) merged.push(movies[i]);
            if (series[i]) merged.push(series[i]);
        }
        
        // Deduplicate objects by imdbId
        const seenIds = new Set();
        const uniqueMerged = [];
        for (const item of merged) {
            if (item && item.imdbId && !seenIds.has(item.imdbId)) {
                seenIds.add(item.imdbId);
                uniqueMerged.push(item);
            }
        }
        
        let finalTrending = uniqueMerged.slice(0, 8);
        
        let isSuccess = true;
        if (finalTrending.length === 0) {
            finalTrending = [
                { name: "Inception", year: "2010", type: "movie", imdbId: "tt1375666" },
                { name: "Breaking Bad", year: "2008-2013", type: "series", imdbId: "tt0903747" },
                { name: "Interstellar", year: "2014", type: "movie", imdbId: "tt0816692" },
                { name: "Game of Thrones", year: "2011-2019", type: "series", imdbId: "tt0944947" },
                { name: "The Matrix", year: "1999", type: "movie", imdbId: "tt0133093" },
                { name: "Stranger Things", year: "2016-", type: "series", imdbId: "tt5027774" }
            ];
            isSuccess = false; // Do not cache long if we got an empty result
        }
        
        if (isSuccess) {
            trendingCache = finalTrending;
            trendingCacheTime = now;
        }
        
        res.json({ success: true, trending: finalTrending });'''

if target_trending_api in content:
    content = content.replace(target_trending_api, replacement_trending_api)
    print("Success: Patched /api/trending route.")
else:
    print("Warning: /api/trending target not matched exactly.")

# 2. Modify /api/recommend parameter parsing to accept imdbId
target_params = '''    const movie = req.body.movie;
    const language = req.body.language || userPrefs.language || 'en';'''

replacement_params = '''    const movie = req.body.movie;
    const imdbId = req.body.imdbId || '';
    const language = req.body.language || userPrefs.language || 'en';'''

if target_params in content:
    content = content.replace(target_params, replacement_params)
    print("Success: Patched parameter parsing in /api/recommend.")
else:
    print("Warning: target_params not matched.")

# 3. Update searchQueryWithFilters construction
target_searchquery = '''    const normalizedQuery = movie.trim().toLowerCase();
    
    // Construct collision-free composite search query for caching
    let searchQueryWithFilters = normalizedQuery;
    if (afterYear || minRating || excludeGenres || favoriteGenres || defaultType !== 'any' || surpriseMe) {
        const y = afterYear ? `y:${afterYear}` : '';
        const r = minRating ? `r:${minRating}` : '';
        const e = excludeGenres ? `e:${excludeGenres.toLowerCase().trim()}` : '';
        const f = favoriteGenres ? `f:${favoriteGenres.toLowerCase().trim()}` : '';
        const t = defaultType !== 'any' ? `t:${defaultType}` : '';
        const s = surpriseMe ? 's:true' : '';
        searchQueryWithFilters = `${normalizedQuery}||${y}||${r}||${e}||${f}||${t}||${s}`;
    }'''

replacement_searchquery = '''    const normalizedQuery = movie.trim().toLowerCase();
    
    // Construct collision-free composite search query for caching
    let searchQueryWithFilters = imdbId ? `${imdbId}||${normalizedQuery}` : normalizedQuery;
    if (afterYear || minRating || excludeGenres || favoriteGenres || defaultType !== 'any' || surpriseMe) {
        const y = afterYear ? `y:${afterYear}` : '';
        const r = minRating ? `r:${minRating}` : '';
        const e = excludeGenres ? `e:${excludeGenres.toLowerCase().trim()}` : '';
        const f = favoriteGenres ? `f:${favoriteGenres.toLowerCase().trim()}` : '';
        const t = defaultType !== 'any' ? `t:${defaultType}` : '';
        const s = surpriseMe ? 's:true' : '';
        searchQueryWithFilters = `${imdbId ? imdbId + '||' : ''}${normalizedQuery}||${y}||${r}||${e}||${f}||${t}||${s}`;
    }'''

if target_searchquery in content:
    content = content.replace(target_searchquery, replacement_searchquery)
    print("Success: Patched searchQueryWithFilters cache key logic.")
else:
    print("Warning: target_searchquery not matched.")

# 4. Update cinemetaPromise concurrent call and verifiedData selection in /api/recommend
target_verification = '''    // Start verification and Gemini fetch concurrently!
    const cinemetaPromise = Promise.all([
        fetchCinemetaData(movie, 'movie'),
        fetchCinemetaData(movie, 'series')
    ]);'''

replacement_verification = '''    // Start verification and Gemini fetch concurrently!
    const cinemetaPromise = imdbId 
        ? fetchCinemetaMeta(imdbId, defaultType === 'any' ? (req.body.type || 'series') : defaultType).then(meta => [meta, null])
        : Promise.all([
            fetchCinemetaData(movie, 'movie'),
            fetchCinemetaData(movie, 'series')
        ]);'''

if target_verification in content:
    content = content.replace(target_verification, replacement_verification)
    print("Success: Patched cinemetaPromise verification call.")
else:
    print("Warning: target_verification not matched.")

# 5. Update verifiedData evaluation logic to handle imdbId cases smoothly
target_evaluation = '''        let verifiedData = null;
        const queryLower = movie.trim().toLowerCase();
        const isMovieExact = movieVerify && movieVerify.name && movieVerify.name.trim().toLowerCase() === queryLower;
        const isSeriesExact = seriesVerify && seriesVerify.name && seriesVerify.name.trim().toLowerCase() === queryLower;

        if (isSeriesExact && !isMovieExact) {
            verifiedData = seriesVerify;
        } else if (isMovieExact && !isSeriesExact) {
            verifiedData = movieVerify;
        } else {
            if (defaultType === 'series') {
                verifiedData = seriesVerify || movieVerify;
            } else if (defaultType === 'movie') {
                verifiedData = movieVerify || seriesVerify;
            } else {
                verifiedData = movieVerify || seriesVerify;
            }
        }'''

replacement_evaluation = '''        let verifiedData = null;
        if (imdbId) {
            verifiedData = movieVerify; // Since we resolved [meta, null], movieVerify contains the exact meta
        } else {
            const queryLower = movie.trim().toLowerCase();
            const isMovieExact = movieVerify && movieVerify.name && movieVerify.name.trim().toLowerCase() === queryLower;
            const isSeriesExact = seriesVerify && seriesVerify.name && seriesVerify.name.trim().toLowerCase() === queryLower;

            if (isSeriesExact && !isMovieExact) {
                verifiedData = seriesVerify;
            } else if (isMovieExact && !isSeriesExact) {
                verifiedData = movieVerify;
            } else {
                if (defaultType === 'series') {
                    verifiedData = seriesVerify || movieVerify;
                } else if (defaultType === 'movie') {
                    verifiedData = movieVerify || seriesVerify;
                } else {
                    verifiedData = movieVerify || seriesVerify;
                }
            }
        }'''

if target_evaluation in content:
    content = content.replace(target_evaluation, replacement_evaluation)
    print("Success: Patched verifiedData evaluation logic.")
else:
    print("Warning: target_evaluation not matched.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished server patches.")
