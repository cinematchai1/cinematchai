import io

index_path = r"public/index.html"
server_path = r"server.js"

with io.open(index_path, "r", encoding="utf-8") as f:
    index_content = f.read()

with io.open(server_path, "r", encoding="utf-8") as f:
    server_content = f.read()

# 1. Fix the input fields clipping by changing the grid in index.html
# Find: <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
target_grid = '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">'
replacement_grid = '<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">'
index_content = index_content.replace(target_grid, replacement_grid)

# 2. Fix the Surprise Me button styling
target_toggle = '<div class="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 peer-checked:after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500 theme-accent-bg"></div>'
replacement_toggle = '<div class="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 peer-checked:after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500"></div>'
index_content = index_content.replace(target_toggle, replacement_toggle)

# 3. Update Load More limit in index.html
target_limit = 'limit: isLoadMore ? 10 : 5,'
replacement_limit = 'limit: 5,'
index_content = index_content.replace(target_limit, replacement_limit)

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(index_content)

# SERVER.JS FIXES

# 1. Update limit logic in server.js
target_server_limit = 'const limit = 10; // Request exactly 10 recommendations pool from Gemini to support the "Load More" button seamlessly'
replacement_server_limit = 'const limit = req.body.limit || 5; // Request exact limit (default 5)'
server_content = server_content.replace(target_server_limit, replacement_server_limit)

# 2. Remove default hidden gems from system instruction
target_instruction = 'Follow these strict rules:\\n1. CURATION BALANCE: Deliver a mix of 70% highly acclaimed mainstream blockbusters/classics and 30% stunning, critically-acclaimed hidden indie gems or cult classics related to the search.\\n2. PLOTS: Keep every localized plot summary (\\'p\\') extremely engaging'
replacement_instruction = 'Follow these strict rules:\\n1. PLOTS: Keep every localized plot summary (\\'p\\') extremely engaging'
server_content = server_content.replace(target_instruction, replacement_instruction)

# 3. Update surpriseMe to add the rule dynamically instead
target_surprise = "if (surpriseMe) {\n        filterConstraints += ` mix in 2-3 extremely obscure, highly-rated hidden indie gems or cult classics related to the search theme to surprise the user;`;\n    }"
replacement_surprise = "if (surpriseMe) {\n        filterConstraints += `\\nCRITICAL RULE: Deliver a mix of highly acclaimed mainstream hits and strictly 2-3 extremely obscure, critically-acclaimed hidden indie gems or cult classics related to the search to surprise the user.`;\n    }"
server_content = server_content.replace(target_surprise, replacement_surprise)

# 4. Update the slicing and hasMore logic in server.js
target_slice = 'const recsToProcess = finalParsed.recommendations.slice(0, 5);'
replacement_slice = 'const recsToProcess = finalParsed.recommendations;'
server_content = server_content.replace(target_slice, replacement_slice)

target_has_more_1 = 'hasMore: finalParsed.recommendations.length > 5,'
replacement_has_more_1 = 'hasMore: finalParsed.recommendations.length >= limit,'
server_content = server_content.replace(target_has_more_1, replacement_has_more_1)

# Fix cache save: don't save raw_recommendations if we don't have extra. Just save updatedRecommendations
target_cache_insert = 'JSON.stringify(finalParsed.recommendations)]'
replacement_cache_insert = 'JSON.stringify(updatedRecommendations)]'
server_content = server_content.replace(target_cache_insert, replacement_cache_insert)

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(server_content)
