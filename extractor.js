const fs = require('fs');
const html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if(scriptMatch) {
    fs.writeFileSync('/root/temp.js', scriptMatch[1]);
    console.log("Extract successful. Linting...");
} else {
    console.log("No script tag found!");
}
