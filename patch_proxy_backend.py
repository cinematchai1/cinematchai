import io

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

target_routes = '''// PUBLIC SHARE RETRIEVAL ENDPOINT
app.get('/api/share/:id', async (req, res) => {'''

replacement_routes = '''// SAME-ORIGIN CINEMETA PROXY ENDPOINTS
app.get('/api/proxy/catalog/:type/:query', async (req, res) => {
    try {
        const type = req.params.type;
        const query = req.params.query;
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/catalog/${cleanType}/top/${query}.json`;
        
        https.get(url, (apiRes) => {
            res.setHeader('Content-Type', 'application/json');
            apiRes.pipe(res);
        }).on('error', (err) => {
            res.status(500).json({ error: 'Proxy fetch failed' });
        });
    } catch(e) {
        res.status(500).json({ error: 'Proxy error' });
    }
});

app.get('/api/proxy/meta/:type/:id', async (req, res) => {
    try {
        const type = req.params.type;
        const id = req.params.id;
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/meta/${cleanType}/${id}.json`;
        
        https.get(url, (apiRes) => {
            res.setHeader('Content-Type', 'application/json');
            apiRes.pipe(res);
        }).on('error', (err) => {
            res.status(500).json({ error: 'Proxy fetch failed' });
        });
    } catch(e) {
        res.status(500).json({ error: 'Proxy error' });
    }
});

// PUBLIC SHARE RETRIEVAL ENDPOINT
app.get('/api/share/:id', async (req, res) => {'''

if target_routes in content:
    content = content.replace(target_routes, replacement_routes)
    print("Success: Added /api/proxy endpoints to server.js.")
else:
    print("Warning: Target share retrieval endpoint in server.js not matched.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)
