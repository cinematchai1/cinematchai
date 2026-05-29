$content = Get-Content 'public/index.html' -Raw

$oldFunc = '        async function getRecommendations(title, isLoadMore = false) {
            let errorDiv = document.getElementById(''error'');
            
            if (!isLoadMore) {
                document.getElementById(''loading'').style.display = ''block'';
                document.getElementById(''results'').innerHTML = '''';
                errorDiv.style.display = ''none'';
            }

            const payload = { 
                title, 
                language: currentLanguage,
                afterYear: document.getElementById(''afterYear'').value,
                minRating: document.getElementById(''minRating'').value,
                excludeGenres: Array.from(document.querySelectorAll(''.genre-checkbox:checked'')).map(cb => cb.value)
            };

            try {
                const response = await fetch(''/api/recommend'', {
                    method: ''POST'',
                    headers: { ''Content-Type'': ''application/json'' },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || ''Failed to fetch recommendations'');
                }

                if (isLoadMore) {
                    currentDisplayCount += 5;
                    const nextBatch = allRecommendations.slice(currentDisplayCount - 5, currentDisplayCount);
                    await renderRecommendations(nextBatch, true);
                    if (currentDisplayCount >= allRecommendations.length) {
                        document.getElementById(''loadMoreContainer'').style.display = ''none'';
                    }
                } else {
                    allRecommendations = data.recs;
                    currentDisplayCount = 5;
                    await renderRecommendations(allRecommendations.slice(0, 5), false);
                    if (allRecommendations.length > 5) {
                        document.getElementById(''loadMoreContainer'').style.display = ''block'';
                    } else {
                        document.getElementById(''loadMoreContainer'').style.display = ''none'';
                    }
                    document.getElementById(''loading'').style.display = ''none'';
                }
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.style.display = ''block'';
                document.getElementById(''loading'').style.display = ''none'';
            }
        }'

$newFunc = '        async function getRecommendations(title, isLoadMore = false) {
            let errorDiv = document.getElementById(''error'');
            let loadBtn = document.getElementById(''loadBtn'');
            let loadMoreContainer = document.getElementById(''loadMoreContainer'');
            
            if (!isLoadMore) {
                document.getElementById(''loading'').style.display = ''block'';
                document.getElementById(''results'').innerHTML = '''';
                errorDiv.style.display = ''none'';
                allRecommendations = [];
                currentDisplayCount = 0;
                loadMoreContainer.style.display = ''none'';
            } else {
                loadBtn.textContent = ''Loading...'';
                loadBtn.disabled = true;
            }

            const excludeTitles = allRecommendations.map(r => r.o);

            const payload = { 
                title, 
                language: currentLanguage,
                afterYear: document.getElementById(''afterYear'').value,
                minRating: document.getElementById(''minRating'').value,
                excludeGenres: Array.from(document.querySelectorAll(''.genre-checkbox:checked'')).map(cb => cb.value),
                limit: isLoadMore ? 10 : 5,
                excludeTitles: excludeTitles
            };

            try {
                const response = await fetch(''/api/recommend'', {
                    method: ''POST'',
                    headers: { ''Content-Type'': ''application/json'' },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || ''Failed to fetch recommendations'');
                }

                if (isLoadMore) {
                    allRecommendations = allRecommendations.concat(data.recs);
                    const nextBatch = allRecommendations.slice(currentDisplayCount, currentDisplayCount + 5);
                    currentDisplayCount += nextBatch.length;
                    await renderRecommendations(nextBatch, true);
                    
                    if (allRecommendations.length > currentDisplayCount) {
                        loadMoreContainer.style.display = ''block'';
                    } else {
                        loadMoreContainer.style.display = ''none'';
                    }
                    loadBtn.textContent = ''Load 5 more suggestions'';
                    loadBtn.disabled = false;
                } else {
                    allRecommendations = data.recs;
                    currentDisplayCount = Math.min(5, allRecommendations.length);
                    await renderRecommendations(allRecommendations.slice(0, currentDisplayCount), false);
                    
                    // Show load more button anyway if we fetched 5, because we assume there might be more
                    if (allRecommendations.length >= 5) {
                        loadMoreContainer.style.display = ''block'';
                    } else {
                        loadMoreContainer.style.display = ''none'';
                    }
                    document.getElementById(''loading'').style.display = ''none'';
                }
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.style.display = ''block'';
                document.getElementById(''loading'').style.display = ''none'';
                if (isLoadMore) {
                    loadBtn.textContent = ''Retry'';
                    loadBtn.disabled = false;
                }
            }
        }'

$content = $content.Replace($oldFunc, $newFunc)
Set-Content 'public/index.html' $content
