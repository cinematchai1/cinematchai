$content = Get-Content 'public/index.html' -Raw
$content = $content -replace 'if \(allRecommendations\.length >= 5\) \{', 'if (allRecommendations.length > 0) {'
$content = $content -replace 'if \(allRecommendations\.length > currentDisplayCount\) \{', 'if (true) { // always show to allow fetching more'
Set-Content 'public/index.html' $content
