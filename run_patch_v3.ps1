Add-Type -Path "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\net462\Renci.SshNet.dll"

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request.IndexOf("Password", [System.StringComparison]::InvariantCultureIgnoreCase) -ne -1) {
            $prompt.Response = $password
        }
    }
})

$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)

$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$nodeScript = @"
const fs = require('fs');
let server = fs.readFileSync('/root/movie-app/server.js', 'utf8');

server = server.replace('const { movie, language, afterYear, minRating, excludeGenres } = req.body;', 
'const { movie, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;');

server = server.replace('Provide recommendations similar to this `\$\{verifiedType\}` (15 recs max).', 
'`\$\{excludeTitles.length > 0 ? \`"Do NOT recommend these exact titles: \`" + excludeTitles.join(\`", \`") + \`". \`" : \`"\`"\}Provide recommendations similar to this `\$\{verifiedType\}` (`\$\{limit\}` recs max).');

server = server.replace('description: `"15 recommendations max`"', 'description: `"Max recommendations returned`"');
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
                        const omdbRes = await fetch(\`http://www.omdbapi.com/?t=\`\$\{encodeURIComponent(rec.originalTitle || rec.title)\}\`&y=\`\$\{rec.year\}\`&apikey=\`\$\{process.env.OMDB_API_KEY\}\`);
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
"@

$cmd1 = $ssh.RunCommand("curl -sL -A 'Mozilla/5.0' https://dpaste.com/AFRZ4864W.txt -o /root/movie-app/public/index.html")
$cmd2 = $ssh.RunCommand("curl -sL -A 'Mozilla/5.0' https://dpaste.com/5DJJ7SQGL.txt -o /root/movie-app/server.js")

$cmd3 = $ssh.RunCommand("echo `"$nodeScript`" | base64 -w 0")
$remoteCmd = "echo `"" + $cmd3.Result + "`" | base64 -d > /root/movie-app/patch_v3.js && node /root/movie-app/patch_v3.js && pm2 restart movie-app"
$cmd4 = $ssh.RunCommand($remoteCmd)

Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd4.Result

$ssh.Disconnect()
$ssh.Dispose()
