const fetch = require('node-fetch');

async function test() {
    const res = await fetch('http://116.203.230.103/api/details/movie/tt1375666');
    const data = await res.json();
    console.log("Type of omdb:", typeof data.omdb);
    console.log("Is array?", Array.isArray(data.omdb));
    if (typeof data.omdb === 'string') {
        console.log("It's a string! Let's try parsing it.");
        try {
            const parsed = JSON.parse(data.omdb);
            console.log("Parsed ratings:", parsed.Ratings);
        } catch(e) {
            console.log("Parse error");
        }
    } else {
        console.log("Ratings:", data.omdb ? data.omdb.Ratings : 'omdb is null');
    }
}
test();
