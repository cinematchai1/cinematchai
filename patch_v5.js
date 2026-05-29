const fs = require('fs');

let html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');

// 1. Dynamic Loading Text
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

// 2. Fix the POST request to include limit and excludeTitles
let replaceFrom = `                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres
                    })
                });`;

let replaceTo = `                const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData && lastMovieData.recommendations ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });`;

html = html.replace(replaceFrom, replaceTo);

// 3. Fix the response handling to append
let resFrom = `                            lastMovieData = data;
                            currentCacheId = data.cacheId;
                            currentOffset = data.recommendations.length;
                            hasMoreResults = data.hasMore || false;
                            try { localStorage.setItem(cacheKey, JSON.stringify(data)); } catch(e){}
                            renderMovies(data.referenceMovie, data.recommendations, data.cacheId);`;

let resTo = `                        if (isLoadMore) {
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
                        }`;

html = html.replace(resFrom, resTo);

// 3.5 FIX THE SYNTAX ERROR (closing bracket of event listener)
let closingFrom = `            } finally {
                btnText.classList.remove('hidden');
                btnLoader.classList.add('hidden');
                searchBtn.disabled = false;
            }
        });`;
let closingTo = `            } finally {
                btnText.classList.remove('hidden');
                btnLoader.classList.add('hidden');
                searchBtn.disabled = false;
            }
        }`;
html = html.replace(closingFrom, closingTo);

// 4. Fix Load More button
let lmFrom = `        btnLoadMore.addEventListener('click', async () => {
            if (!currentCacheId || !hasMoreResults) return;
            
            loadMoreText.classList.add('hidden');
            loadMoreSpinner.classList.remove('hidden');
            btnLoadMore.disabled = true;
            
            try {
                const response = await fetch('/api/recommend/more', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cacheId: currentCacheId, offset: currentOffset })
                });
                
                if (response.status === 401) {
                    setLoginState(false);
                    openModal('login');
                    return;
                }
                
                const data = await response.json();
                if (data.recommendations && data.recommendations.length > 0) {
                    renderMovies(null, data.recommendations, currentCacheId, true);
                    hasMoreResults = data.hasMore;
                    currentOffset += data.recommendations.length;
                } else {
                    hasMoreResults = false;
                    btnLoadMore.classList.add('hidden');
                }
            } catch (err) {
                console.error(err);
            } finally {
                loadMoreText.classList.remove('hidden');
                loadMoreSpinner.classList.add('hidden');
                btnLoadMore.disabled = false;
            }
        });`;

let lmTo = `        btnLoadMore.addEventListener('click', async () => {
            loadMoreText.classList.add('hidden');
            loadMoreSpinner.classList.remove('hidden');
            btnLoadMore.disabled = true;
            await performSearch(true);
            loadMoreText.classList.remove('hidden');
            loadMoreSpinner.classList.add('hidden');
            btnLoadMore.disabled = false;
        });`;

html = html.replace(lmFrom, lmTo);

// 5. Fix posterUrl
html = html.replace('const posterUrl = (r.poster && r.poster !== \'N/A\') ? r.poster : `https://images.metahub.space/poster/small/${r.imdbId}/img`;', 'const posterUrl = r.posterUrl ? r.posterUrl : (r.poster && r.poster !== \'N/A\' ? r.poster : (r.imdbId ? `https://images.metahub.space/poster/small/${r.imdbId}/img` : \'https://via.placeholder.com/300x450?text=Sem+Poster\'));');
html = html.replace('<img src="https://images.metahub.space/poster/small/${r.imdbId}/img"', '<img src="${posterUrl}"');

// 6. Loading Text triggers
html = html.replace('loadingIndicator.classList.remove(\'hidden\');', 'loadingIndicator.classList.remove(\'hidden\'); startLoadingText();');
html = html.replace('loadingIndicator.classList.add(\'hidden\');', 'loadingIndicator.classList.add(\'hidden\'); stopLoadingText();');

fs.writeFileSync('/root/movie-app/public/index.html', html);
console.log('Patch complete.');
