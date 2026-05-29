import io

server_path = r"server.js"

with io.open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

target_block = '''        const [[movieVerify, seriesVerify], body] = await Promise.all([cinemetaPromise, geminiPromise]);

        const verifiedData = movieVerify || seriesVerify;'''

replacement_block = '''        const [[movieVerify, seriesVerify], body] = await Promise.all([cinemetaPromise, geminiPromise]);

        let verifiedData = null;
        const queryLower = movie.trim().toLowerCase();
        const isMovieExact = movieVerify && movieVerify.name && movieVerify.name.trim().toLowerCase() === queryLower;
        const isSeriesExact = seriesVerify && seriesVerify.name && seriesVerify.name.trim().toLowerCase() === queryLower;

        if (isSeriesExact && !isMovieExact) {
            verifiedData = seriesVerify;
        } else if (isMovieExact && !isSeriesExact) {
            verifiedData = movieVerify;
        } else {
            if (defaultType === 'series') {
                verifiedData = seriesVerify || movieVerify;
            } else if (defaultType === 'movie') {
                verifiedData = movieVerify || seriesVerify;
            } else {
                verifiedData = movieVerify || seriesVerify;
            }
        }'''

if target_block in content:
    content = content.replace(target_block, replacement_block)
    print("Success: Patched exact title matching prioritization logic in server.js.")
else:
    print("Warning: Target verification block in server.js not matched exactly.")

with io.open(server_path, "w", encoding="utf-8") as f:
    f.write(content)
