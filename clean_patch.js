const fs = require('fs');
let server = fs.readFileSync('/root/movie-app/server.js', 'utf8');

server = server.replace('const { movie, language, afterYear, minRating, excludeGenres } = req.body;', 
'const { movie, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;');

server = server.replace('Provide recommendations similar to this ${verifiedType} (15 recs max).', 
'${excludeTitles.length > 0 ? `Do NOT recommend these exact titles: ` + excludeTitles.join(`, `) + `. ` : ``}Provide recommendations similar to this ${verifiedType} (${limit} recs max).');

server = server.replace('description: "15 recommendations max"', 'description: "Max recommendations returned"');
server = server.replace('hasMore: finalParsed.recommendations.length > 5,', 'hasMore: true,');

let originalCinemetaBlock = `                const recsToProcess = finalParsed.recommendations.slice(0, 5);
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
                }));`;

let newCinemetaBlock = `                const recsToProcess = finalParsed.recommendations.slice(0, limit);
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
                    try {
                        const omdbRes = await fetch(\`http://www.omdbapi.com/?t=\${encodeURIComponent(rec.originalTitle || rec.title)}&y=\${rec.year}&apikey=\${process.env.OMDB_API_KEY}\`);
                        const omdbData = await omdbRes.json();
                        if (omdbData.Response === 'True' && omdbData.Poster && omdbData.Poster !== 'N/A') {
                            rec.posterUrl = omdbData.Poster;
                        } else if (!rec.imdbId && omdbData.Response === 'True' && omdbData.imdbID) {
                            rec.imdbId = omdbData.imdbID;
                            if (omdbData.Poster !== 'N/A') rec.posterUrl = omdbData.Poster;
                        }
                    } catch(e) {}
                    return rec;
                }));`;

server = server.replace(originalCinemetaBlock, newCinemetaBlock);
fs.writeFileSync('/root/movie-app/server.js', server);

let html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');

let dynamicLoadingCode = `
        const loadingPhrases = [
            typeof t !== 'undefined' && t.loading ? t.loading : "A carregar...",
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
`;

html = html.replace('searchForm.addEventListener(\'submit\', async (e) => {', dynamicLoadingCode + '\n        searchForm.addEventListener(\'submit\', async (e) => {\n            e.preventDefault();\n            await performSearch();\n        });\n\n        async function performSearch(isLoadMore = false) {');
html = html.replace('e.preventDefault();\n            \n            const movie = searchInput.value.trim();', 'const movie = searchInput.value.trim();');

let payloadStr = `const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };`;

let rgx1 = /const movie = searchInput\.value\.trim\(\);\s*if \(!movie\) return;\s*const afterYear = document\.getElementById\('filter-year'\)\.value;\s*const minRating = document\.getElementById\('filter-rating'\)\.value;\s*const excludeGenres = Array\.from\(document\.querySelectorAll\('\.genre-checkbox:checked'\)\)\.map\(cb => cb\.value\);\s*try \{\s*const response = await fetch\('\/api\/recommend', \{\s*method: 'POST',\s*headers: \{ 'Content-Type': 'application\/json' \},\s*body: JSON\.stringify\(\{ \s*movie, \s*language: currentLang,\s*afterYear,\s*minRating,\s*excludeGenres\s*\}\)\s*\}\);/m;

let repl1 = `const movie = searchInput.value.trim();
            if (!movie) return;

            const afterYear = document.getElementById('filter-year').value;
            const minRating = document.getElementById('filter-rating').value;
            const excludeGenres = Array.from(document.querySelectorAll('.genre-checkbox:checked')).map(cb => cb.value);
            
            ` + payloadStr + `
            
            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });`;

html = html.replace(rgx1, repl1);

let rgx2 = /lastMovieData = data;\s*currentCacheId = data\.cacheId;\s*currentOffset = data\.recommendations\.length;\s*hasMoreResults = data\.hasMore \|\| false;\s*try \{ localStorage\.setItem\(cacheKey, JSON\.stringify\(data\)\); \} catch\(e\)\{\}\s*renderMovies\(data\.referenceMovie, data\.recommendations, data\.cacheId\);/m;
let repl2 = `
                        if (isLoadMore) {
                            lastMovieData.recommendations = lastMovieData.recommendations.concat(data.recommendations);
                            renderMovies(null, data.recommendations, data.cacheId, true);
                            hasMoreResults = data.hasMore || false;
                        } else {
                            lastMovieData = data;
                            currentCacheId = data.cacheId;
                            currentOffset = data.recommendations.length;
                            hasMoreResults = data.hasMore || false;
                            try { localStorage.setItem(cacheKey, JSON.stringify(data)); } catch(e){}
                            renderMovies(data.referenceMovie, data.recommendations, data.cacheId);
                        }
`;
html = html.replace(rgx2, repl2);

let rgx3 = /btnLoadMore\.addEventListener\('click', async \(\) => \{[\s\S]*?\}\);/m;
let repl3 = `
        btnLoadMore.addEventListener('click', async () => {
            loadMoreText.classList.add('hidden');
            loadMoreSpinner.classList.remove('hidden');
            btnLoadMore.disabled = true;
            await performSearch(true);
            loadMoreText.classList.remove('hidden');
            loadMoreSpinner.classList.add('hidden');
            btnLoadMore.disabled = false;
        });
`;
html = html.replace(rgx3, repl3);

html = html.replace('const posterUrl = (r.poster && r.poster !== \'N/A\') ? r.poster : `https://images.metahub.space/poster/small/${r.imdbId}/img`;', 'const posterUrl = r.posterUrl ? r.posterUrl : (r.poster && r.poster !== \'N/A\' ? r.poster : (r.imdbId ? `https://images.metahub.space/poster/small/${r.imdbId}/img` : \'https://via.placeholder.com/300x450?text=Sem+Poster\'));');
html = html.replace('<img src="https://images.metahub.space/poster/small/${r.imdbId}/img"', '<img src="${posterUrl}"');
html = html.replace('loadingIndicator.classList.remove(\'hidden\');', 'loadingIndicator.classList.remove(\'hidden\'); startLoadingText();');
html = html.replace('loadingIndicator.classList.add(\'hidden\');', 'loadingIndicator.classList.add(\'hidden\'); stopLoadingText();');

fs.writeFileSync('/root/movie-app/public/index.html', html);
