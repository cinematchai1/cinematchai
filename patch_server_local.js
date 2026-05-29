const fs = require('fs');
let content = fs.readFileSync('server.js', 'utf8');

// Change limit back to 5 for initial request
content = content.replace('const { title, language, afterYear, minRating, excludeGenres, limit = 5, excludeTitles = [] } = req.body;', 'const { movie, language, afterYear, minRating, excludeGenres } = req.body;');

// Wait, the original server.js doesn't have title, it has movie!
// Let me just restore server.js to the pristine state first, then apply my changes.
