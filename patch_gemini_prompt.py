import io

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update promptText to ask for 12 recommendations max
target_prompttext = '''    const promptText = `User requested recommendations for the movie/series: "${movie}". Language: ${language === 'pt' ? 'pt-PT' : 'en'}.
${filterConstraints ? `Additional filter constraints for the recommended items:${filterConstraints}` : ''}
Provide recommendations similar to this movie/series (15 recs max).`;'''

replacement_prompttext = '''    const promptText = `User requested recommendations for the movie/series: "${movie}". Language: ${language === 'pt' ? 'pt-PT' : 'en'}.
${filterConstraints ? `Additional filter constraints for the recommended items:${filterConstraints}` : ''}
Provide recommendations similar to this movie/series (12 recs max).`;'''

if target_prompttext in content:
    content = content.replace(target_prompttext, replacement_prompttext)
    print("Success: Updated promptText to 12 recommendations treshold.")
else:
    print("Warning: target_prompttext not matched.")

# 2. Update responseSchema recommendations count
target_schema_recs = '''            recs: {
                type: "ARRAY",
                description: "15 recommendations max",'''

replacement_schema_recs = '''            recs: {
                type: "ARRAY",
                description: "12 recommendations max",'''

if target_schema_recs in content:
    content = content.replace(target_schema_recs, replacement_schema_recs)
    print("Success: Updated responseSchema recommendations description.")
else:
    print("Warning: target_schema_recs not matched.")

# 3. Update systemInstruction and generationConfig in the JSON payload
target_payload = '''    const postData = JSON.stringify({
        systemInstruction: {
            parts: [{ text: "You are an expert movie recommendation engine and professional film critic. Your recommendations must be extremely curated, mixing obvious blockbusters with hidden indie gems to surprise the user. Ensure strict adherence to user preferences." }]
        },
        contents: [{ parts: [{ text: promptText }] }],
        generationConfig: { 
            temperature: 0.7,
            responseMimeType: "application/json",
            responseSchema: responseSchema
        }
    });'''

replacement_payload = '''    const postData = JSON.stringify({
        systemInstruction: {
            parts: [{ text: "You are a world-class film critic and highly sophisticated movie recommendation engine. Analyze the user\\'s reference title based on emotional tone, aesthetic style, thematic subtext, and pacing.\\n\\nFollow these strict rules:\\n1. CURATION BALANCE: Deliver a mix of 70% highly acclaimed mainstream blockbusters/classics and 30% stunning, critically-acclaimed hidden indie gems or cult classics related to the search.\\n2. PLOTS: Keep every localized plot summary (\\'p\\') extremely engaging, punchy, and limited to a MAXIMUM of 2-3 sentences. Never write long descriptions.\\n3. LOCALIZATION: Translate localized titles (\\'t\\') and plot summaries (\\'p\\') beautifully into natural, contextual Portuguese (pt-PT) if requested, avoiding Brazilian Portuguese terminology (e.g. use \\'ecrã\\' instead of \\'tela\\', \\'género\\' instead of \\'gênero\\').\\n4. IMDB ID ACCURACY: Ensure the provided \\'imdb_id\\' is the actual, correct IMDB ID (starting with \\'tt\\') for that specific title. Search your knowledge base and verify it. Never hallucinate IDs." }]
        },
        contents: [{ parts: [{ text: promptText }] }],
        generationConfig: { 
            temperature: surpriseMe ? 0.8 : 0.4,
            responseMimeType: "application/json",
            responseSchema: responseSchema
        }
    });'''

if target_payload in content:
    content = content.replace(target_payload, replacement_payload)
    print("Success: Patched systemInstruction and generationConfig temperature parameters in server.js.")
else:
    print("Warning: target_payload in server.js not matched exactly.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished prompt patches.")
