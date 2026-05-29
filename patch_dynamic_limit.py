import io

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Parse limit from req.body
target_params = '''    const movie = req.body.movie;
    const imdbId = req.body.imdbId || '';
    const language = req.body.language || userPrefs.language || 'en';'''

replacement_params = '''    const movie = req.body.movie;
    const imdbId = req.body.imdbId || '';
    const language = req.body.language || userPrefs.language || 'en';
    const limit = parseInt(req.body.limit, 10) || 5;'''

if target_params in content:
    content = content.replace(target_params, replacement_params)
    print("Success: Parsed limit from request body.")
else:
    print("Warning: target_params not found in server.js.")

# 2. Update promptText construction to use dynamic limit
target_prompt = '''    const promptText = `User requested recommendations for the movie/series: "${movie}". Language: ${language === 'pt' ? 'pt-PT' : 'en'}.
${filterConstraints ? `Additional filter constraints for the recommended items:${filterConstraints}` : ''}
Provide recommendations similar to this movie/series (12 recs max).`;'''

replacement_prompt = '''    const promptText = `User requested recommendations for the movie/series: "${movie}". Language: ${language === 'pt' ? 'pt-PT' : 'en'}.
${filterConstraints ? `Additional filter constraints for the recommended items:${filterConstraints}` : ''}
Provide recommendations similar to this movie/series (${limit} recs max).`;'''

if target_prompt in content:
    content = content.replace(target_prompt, replacement_prompt)
    print("Success: Updated promptText to use dynamic limit.")
else:
    print("Warning: target_prompt not found in server.js.")

# 3. Update responseSchema recs description to use dynamic limit
target_schema_recs = '''            recs: {
                type: "ARRAY",
                description: "12 recommendations max",'''

replacement_schema_recs = '''            recs: {
                type: "ARRAY",
                description: `${limit} recommendations max`,'''

if target_schema_recs in content:
    content = content.replace(target_schema_recs, replacement_schema_recs)
    print("Success: Updated responseSchema description to use dynamic limit.")
else:
    print("Warning: target_schema_recs not found in server.js.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished dynamic limit patches.")
