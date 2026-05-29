$content = Get-Content 'server.js' -Raw
$content = $content -replace 'const \{ title, language, afterYear, minRating, excludeGenres \} = req.body;', 'const { title, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;'
$content = $content -replace 'Provide recommendations similar to this \$\{verifiedType\} \(15 recs max\).', '\$\{excludeTitles.length > 0 ? "Do NOT recommend these titles: \$\{excludeTitles.join(, )\}" : ""\} Provide recommendations similar to this \$\{verifiedType\} (\$\{limit\} recs max).'
$content = $content -replace 'description: "15 recommendations max"', 'description: "Max recommendations returned"'
Set-Content 'server.js' $content
