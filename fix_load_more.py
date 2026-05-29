import io

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update cache hit check to retrieve raw_recommendations and return hasMore properly
target_cache_hit = '''        // Check cache first (valid for 7 days)
        const cacheResult = await pool.query(
            `SELECT id, reference_movie, recommendations FROM recommendation_cache 
             WHERE search_query = $1 AND language = $2 AND created_at > NOW() - INTERVAL '7 days'`,
            [searchQueryWithFilters, language]
        );

        if (cacheResult.rows.length > 0) {
            console.log(`[CACHE HIT] Returning cached recommendations for: ${searchQueryWithFilters} (${language})`);
            return res.json({
                cacheId: cacheResult.rows[0].id,
                referenceMovie: cacheResult.rows[0].reference_movie,
                recommendations: cacheResult.rows[0].recommendations
            });
        }'''

replacement_cache_hit = '''        // Check cache first (valid for 7 days)
        const cacheResult = await pool.query(
            `SELECT id, reference_movie, recommendations, raw_recommendations FROM recommendation_cache 
             WHERE search_query = $1 AND language = $2 AND created_at > NOW() - INTERVAL '7 days'`,
            [searchQueryWithFilters, language]
        );

        if (cacheResult.rows.length > 0) {
            const rawRecs = cacheResult.rows[0].raw_recommendations || [];
            const processedRecs = cacheResult.rows[0].recommendations || [];
            console.log(`[CACHE HIT] Returning cached recommendations for: ${searchQueryWithFilters} (${language})`);
            return res.json({
                cacheId: cacheResult.rows[0].id,
                referenceMovie: cacheResult.rows[0].reference_movie,
                recommendations: processedRecs,
                hasMore: rawRecs.length > processedRecs.length,
                totalCached: rawRecs.length
            });
        }'''

if target_cache_hit in content:
    content = content.replace(target_cache_hit, replacement_cache_hit)
    print("Success: Updated cache hit query and response fields.")
else:
    print("Warning: target_cache_hit not found in server.js.")

# 2. Update backend limit to be fixed at 10 for the pool (so that initial is 5 and load more is 5)
target_limit_parsing = '''    const language = req.body.language || userPrefs.language || 'en';
    const limit = parseInt(req.body.limit, 10) || 5;'''

replacement_limit_parsing = '''    const language = req.body.language || userPrefs.language || 'en';
    const limit = 10; // Request exactly 10 recommendations pool from Gemini to support the "Load More" button seamlessly'''

if target_limit_parsing in content:
    content = content.replace(target_limit_parsing, replacement_limit_parsing)
    print("Success: Fixed backend recommendation pool limit to 10.")
else:
    print("Warning: target_limit_parsing not found in server.js.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished load more patches.")
