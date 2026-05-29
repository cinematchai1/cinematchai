const fs = require('fs');

let code = fs.readFileSync('server.js', 'utf8');

// Inject fetchOMDB if not exists
if (!code.includes('function fetchOMDB')) {
    const fetchOMDBCode = `
function fetchOMDB(imdbId) {
    return new Promise((resolve) => {
        if (!imdbId) return resolve(null);
        const apiKey = '25c26a4';
        const url = \`http://www.omdbapi.com/?i=\${imdbId}&apikey=\${apiKey}\`;
        const req = require('http').get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(body)); } catch(e) { resolve(null); }
            });
        });
        req.on('error', () => resolve(null));
        req.setTimeout(3000, () => { req.abort(); resolve(null); });
    });
}
`;
    // Insert after fetchTMDBMeta
    code = code.replace(/async function fetchTMDBMeta[\s\S]+?return new Promise[\s\S]+?\}\);\s*\}/, match => match + '\n' + fetchOMDBCode);
}

// Inject /api/details/:type/:id route
if (!code.includes('/api/details/:type/:id')) {
    const detailsRoute = `
// NEW MASTER ENDPOINT (DB CACHE -> TMDB+OMDB -> CINEMETA)
app.get('/api/details/:type/:id', async (req, res) => {
    try {
        const type = req.params.type;
        const id = req.params.id; // IMDb ID
        const lang = req.query.lang || 'en';

        // 1. Check DB Cache
        const cacheQuery = await pool.query('SELECT tmdb_data, omdb_data, cinemeta_data FROM movies_cache WHERE imdb_id = $1', [id]);
        if (cacheQuery.rows.length > 0) {
            const row = cacheQuery.rows[0];
            // If we have TMDB+OMDB or Cinemeta, return it
            if (row.tmdb_data || row.cinemeta_data) {
                return res.json({ success: true, source: 'cache', tmdb: row.tmdb_data, omdb: row.omdb_data, cinemeta: row.cinemeta_data });
            }
        }

        // 2. Not in Cache. Fetch concurrently from TMDB and OMDb
        const [tmdbMeta, omdbMeta] = await Promise.all([
            fetchTMDBMeta(id, type, lang),
            fetchOMDB(id)
        ]);

        let finalData = { tmdb: tmdbMeta, omdb: omdbMeta, cinemeta: null };

        // 3. Fallback to Cinemeta if TMDB fails
        if (!tmdbMeta) {
            const cinemeta = await fetchCinemetaMeta(id, type);
            finalData.cinemeta = cinemeta;
        }

        // Save to DB
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const fallbackTitle = tmdbMeta ? tmdbMeta.name : (finalData.cinemeta ? finalData.cinemeta.name : 'Unknown');
        
        await pool.query(\`
            INSERT INTO movies_cache (imdb_id, title, type, tmdb_data, omdb_data, cinemeta_data)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (imdb_id) DO UPDATE SET
            tmdb_data = EXCLUDED.tmdb_data,
            omdb_data = EXCLUDED.omdb_data,
            cinemeta_data = EXCLUDED.cinemeta_data,
            updated_at = CURRENT_TIMESTAMP
        \`, [id, fallbackTitle, cleanType, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(finalData.cinemeta)]);

        return res.json({ success: true, source: 'api', ...finalData });
    } catch (e) {
        console.error("Details API Error:", e);
        res.status(500).json({ error: 'Server error' });
    }
});
`;
    // Insert before app.get('/api/proxy/catalog...
    code = code.replace('// SAME-ORIGIN CINEMETA PROXY ENDPOINTS', detailsRoute + '\n// SAME-ORIGIN CINEMETA PROXY ENDPOINTS');
}

fs.writeFileSync('server.js', code, 'utf8');
console.log('Backend updated successfully.');
