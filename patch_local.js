const fs = require('fs');

let server = fs.readFileSync('server.js', 'utf8');

// 1. Update /api/recommend endpoint payload
server = server.replace('const { movie, language, afterYear, minRating, excludeGenres } = req.body;', 
'const { movie, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;');

// 2. Update Gemini Prompt
server = server.replace('Provide recommendations similar to this  (15 recs max).', 
'Provide recommendations similar to this  ( recs max).');

server = server.replace('description: "15 recommendations max"', 'description: "Max recommendations returned"');

// 3. Update hasMore
server = server.replace('hasMore: finalParsed.recommendations.length > 5,', 'hasMore: true,');

// 4. Update OMDB Poster Fallback
// We will replace the block inside fetchCinemetaData map
let originalCinemetaBlock =                 const recsToProcess = finalParsed.recommendations.slice(0, 5);
                const updatedRecommendations = await Promise.all(recsToProcess.map(async (rec) => {
                    const data = await fetchCinemetaData(rec.originalTitle || rec.title, rec.type);
                    if (data) {
                        rec.imdbId = data.imdb_id;
                        const meta = await fetchCinemetaMeta(rec.imdbId, rec.type);
                        if (meta) {
                            rec.tmdbId = meta.moviedb_id || null;
                            if (meta.trailers && meta.trailers.length > 0) {
                                const trailer = meta.trailers.find(t => t.source) || meta.trailers[0];
                                rec.trailerYtId = trailer.source;
                            }
                        }
                    }
                    return rec;
                }));;

let newCinemetaBlock =                 const recsToProcess = finalParsed.recommendations.slice(0, limit);
                const updatedRecommendations = await Promise.all(recsToProcess.map(async (rec) => {
                    const data = await fetchCinemetaData(rec.originalTitle || rec.title, rec.type);
                    if (data) {
                        rec.imdbId = data.imdb_id;
                        const meta = await fetchCinemetaMeta(rec.imdbId, rec.type);
                        if (meta) {
                            rec.tmdbId = meta.moviedb_id || null;
                            if (meta.trailers && meta.trailers.length > 0) {
                                const trailer = meta.trailers.find(t => t.source) || meta.trailers[0];
                                rec.trailerYtId = trailer.source;
                            }
                        }
                    }
                    
                    // OMDB Fallback for poster if we don't trust Metahub or want a direct URL
                    try {
                        const omdbRes = await fetch(\http://www.omdbapi.com/?t=\&y=\&apikey=\\);
                        const omdbData = await omdbRes.json();
                        if (omdbData.Response === 'True' && omdbData.Poster && omdbData.Poster !== 'N/A') {
                            rec.posterUrl = omdbData.Poster;
                        } else if (!rec.imdbId && omdbData.Response === 'True' && omdbData.imdbID) {
                            rec.imdbId = omdbData.imdbID;
                            if (omdbData.Poster !== 'N/A') rec.posterUrl = omdbData.Poster;
                        }
                    } catch(e) {}

                    return rec;
                }));;

server = server.replace(originalCinemetaBlock, newCinemetaBlock);

fs.writeFileSync('server_fixed.js', server);

// ------------------------------------------------------------
// Fix index.html
let html = fs.readFileSync('public/index.html', 'utf8');

// A. Dynamic Loading Text
let dynamicLoadingCode = 
        const loadingPhrases = [
            t.loading || "A carregar...",
            "A preparar as pipocas...",
            "A escurecer a sala...",
            "A consultar os realizadores...",
            "A afinar o som surround...",
            "A rebobinar a fita..."
        ];
        let loadingInterval;
        let phraseIndex = 0;

        function startLoadingText() {
            const loadingText = document.querySelector('#loading span:last-child');
            if(!loadingText) return;
            loadingText.textContent = loadingPhrases[0];
            phraseIndex = 1;
            loadingInterval = setInterval(() => {
                loadingText.textContent = loadingPhrases[phraseIndex];
                phraseIndex = (phraseIndex + 1) % loadingPhrases.length;
            }, 2000);
        }

        function stopLoadingText() {
            clearInterval(loadingInterval);
        }
;

// Insert it before submitSearch
html = html.replace('searchForm.addEventListener(''submit'', async (e) => {', dynamicLoadingCode + '\n        searchForm.addEventListener(''submit'', async (e) => {\n            e.preventDefault();\n            await performSearch();\n        });\n\n        async function performSearch(isLoadMore = false) {');

// Fix e.preventDefault inside performSearch
html = html.replace('e.preventDefault();\n            \n            const movie = searchInput.value.trim();', 'const movie = searchInput.value.trim();');

// B. Limit and ExcludeTitles in payload
let payloadStr = const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };;
html = html.replace(/const movie = searchInput.value.trim\(\);[\s\S]*?body: JSON\.stringify\(\{\s*movie,[\s\S]*?excludeGenres\s*\}\)/m, 'const movie = searchInput.value.trim();\n            if (!movie) return;\n\n            const afterYear = document.getElementById("filter-year").value;\n            const minRating = document.getElementById("filter-rating").value;\n            const excludeGenres = Array.from(document.querySelectorAll(".genre-checkbox:checked")).map(cb => cb.value);\n            \n            ' + payloadStr + '\n            \n            try {\n                const response = await fetch("/api/recommend", {\n                    method: "POST",\n                    headers: { "Content-Type": "application/json" },\n                    body: JSON.stringify(payload)');

// C. Results rendering (append if isLoadMore)
let renderStr = 
                        if (isLoadMore) {
                            lastMovieData.recommendations = lastMovieData.recommendations.concat(data.recommendations);
                            renderMovies(null, data.recommendations, data.cacheId, true);
                        } else {
                            lastMovieData = data;
                            currentCacheId = data.cacheId;
                            currentOffset = data.recommendations.length;
                            hasMoreResults = data.hasMore || false;
                            try { localStorage.setItem(cacheKey, JSON.stringify(data)); } catch(e){}
                            renderMovies(data.referenceMovie, data.recommendations, data.cacheId);
                        }
;
html = html.replace(/lastMovieData = data;[\s\S]*?renderMovies\(data\.referenceMovie, data\.recommendations, data\.cacheId\);/, renderStr);

// D. Load More button calls performSearch
let loadMoreStr = 
        btnLoadMore.addEventListener('click', async () => {
            loadMoreText.classList.add('hidden');
            loadMoreSpinner.classList.remove('hidden');
            btnLoadMore.disabled = true;
            await performSearch(true);
            loadMoreText.classList.remove('hidden');
            loadMoreSpinner.classList.add('hidden');
            btnLoadMore.disabled = false;
        });
;
html = html.replace(/btnLoadMore\.addEventListener\('click', async \(\) => \{[\s\S]*?\}\);/, loadMoreStr);

// E. Fix the poster rendering to use rec.posterUrl if available
html = html.replace('const posterUrl = (r.poster && r.poster !== ''N/A'') ? r.poster : https://images.metahub.space/poster/small//img;', 'const posterUrl = r.posterUrl ? r.posterUrl : (r.poster && r.poster !== ''N/A'' ? r.poster : (r.imdbId ? https://images.metahub.space/poster/small//img : ''https://via.placeholder.com/300x450?text=Sem+Poster''));');
html = html.replace('<img src="https://images.metahub.space/poster/small//img"', '<img src=""');

// F. Start and Stop loading text
html = html.replace('loadingIndicator.classList.remove(''hidden'');', 'loadingIndicator.classList.remove(''hidden''); startLoadingText();');
html = html.replace('loadingIndicator.classList.add(''hidden'');', 'loadingIndicator.classList.add(''hidden''); stopLoadingText();');

fs.writeFileSync('index_fixed.html', html);

console.log('Patched correctly');
