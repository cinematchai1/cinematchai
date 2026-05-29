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

// Patch server.js
let s = fs.readFileSync('/root/movie-app/server.js', 'utf8');
s = s.replace('const { movie, language, afterYear, minRating, excludeGenres } = req.body;', 'const { movie, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;');
s = s.replace('Provide recommendations similar to this ${verifiedType} (15 recs max).', '${excludeTitles.length > 0 ? `"Do NOT recommend these titles: `" + excludeTitles.join(`, `) + `". ` : ``}Provide recommendations similar to this ${verifiedType} (${limit} recs max).');
s = s.replace('hasMore: finalParsed.recommendations.length > 5,', 'hasMore: true,');
s = s.replace('description: "15 recommendations max"', 'description: "Max recommendations returned"');
fs.writeFileSync('/root/movie-app/server.js', s);

// Patch index.html
let html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');

// Replace submitSearch parameters to allow isLoadMore
html = html.replace('searchForm.addEventListener(''submit'', async (e) => {', 'searchForm.addEventListener(''submit'', async (e) => {\n            e.preventDefault();\n            await performSearch();\n        });\n\n        async function performSearch(isLoadMore = false) {');

// Fix e.preventDefault
html = html.replace('e.preventDefault();\n            \n            const movie = searchInput.value.trim();', 'const movie = searchInput.value.trim();');

// Fix payload to send limit and excludeTitles
let payloadStr = `const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    }`;
html = html.replace(/body: JSON\.stringify\(\{\s*movie,[\s\S]*?excludeGenres\s*\}\)/m, 'body: JSON.stringify(payload)');
html = html.replace('const afterYear = document.getElementById(''filter-year'').value;', 'const afterYear = document.getElementById(''filter-year'').value;\n            ' + payloadStr + ';');

// Fix the results rendering logic to append if loadMore
let renderStr = `
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
`;
html = html.replace(/lastMovieData = data;[\s\S]*?renderMovies\(data\.referenceMovie, data\.recommendations, data\.cacheId\);/, renderStr);

// Fix the Load More button to call performSearch
let loadMoreStr = `
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
html = html.replace(/btnLoadMore\.addEventListener\('click', async \(\) => \{[\s\S]*?\}\);/, loadMoreStr);

fs.writeFileSync('/root/movie-app/public/index.html', html);
"@

$cmd = $ssh.RunCommand("cat << 'EOF' > /root/movie-app/patch.js`n" + $nodeScript + "`nEOF`nnode /root/movie-app/patch.js && pm2 restart movie-app")
Write-Host "PATCH OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
$ssh.Dispose()
