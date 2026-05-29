const https = require('https');
require('dotenv').config();

async function fetchTMDBMeta(imdbId, type, language) {
    return new Promise((resolve) => {
        if (!imdbId) return resolve(null);
        const apiKey = process.env.TMDB_API_KEY || 'a371649908276cdfd4448c0585638a77';
        const tmdbLang = language === 'pt' ? 'pt-PT' : 'en-US';
        const tmdbType = (type === 'series' || type === 'tv') ? 'tv' : 'movie';
        
        const url = `https://api.themoviedb.org/3/find/${imdbId}?api_key=${apiKey}&external_source=imdb_id&language=${tmdbLang}`;
        
        const req = https.get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    let result = null;
                    if (tmdbType === 'movie' && data.movie_results && data.movie_results.length > 0) {
                        result = data.movie_results[0];
                    } else if (data.tv_results && data.tv_results.length > 0) {
                        result = data.tv_results[0];
                    }
                    
                    if (!result) return resolve(null);

                    // Fetch full details for runtime/genres
                    const detailsUrl = `https://api.themoviedb.org/3/${tmdbType}/${result.id}?api_key=${apiKey}&language=${tmdbLang}&append_to_response=videos`;
                    https.get(detailsUrl, (res2) => {
                        let body2 = '';
                        res2.on('data', c => body2 += c);
                        res2.on('end', () => {
                            try {
                                const details = JSON.parse(body2);
                                let trailerYtId = null;
                                if (details.videos && details.videos.results && details.videos.results.length > 0) {
                                    const trailer = details.videos.results.find(v => v.type === 'Trailer' && v.site === 'YouTube') || details.videos.results[0];
                                    trailerYtId = trailer.key;
                                }
                                resolve({
                                    title: details.title || details.name || result.title || result.name,
                                    originalTitle: details.original_title || details.original_name || result.original_title || result.original_name,
                                    description: details.overview || result.overview,
                                    year: (details.release_date || details.first_air_date || result.release_date || result.first_air_date || '').substring(0, 4),
                                    poster: details.poster_path ? `https://image.tmdb.org/t/p/w500${details.poster_path}` : (result.poster_path ? `https://image.tmdb.org/t/p/w500${result.poster_path}` : null),
                                    rating: details.vote_average ? details.vote_average.toFixed(1) : (result.vote_average ? result.vote_average.toFixed(1) : null),
                                    category: details.genres ? details.genres.map(g => g.name).join(', ') : '',
                                    duration: tmdbType === 'movie' ? (details.runtime ? `${details.runtime} min` : '') : (details.number_of_seasons ? `${details.number_of_seasons} Seasons` : ''),
                                    type: tmdbType,
                                    imdb_id: imdbId,
                                    tmdbId: details.id,
                                    trailerYtId: trailerYtId
                                });
                            } catch(e) { resolve(null); }
                        });
                    }).on('error', () => resolve(null));

                } catch(e) {
                    resolve(null);
                }
            });
        });
        req.on('error', () => resolve(null));
        req.setTimeout(5000, () => { req.abort(); resolve(null); });
    });
}

fetchTMDBMeta('tt1375666', 'movie', 'pt').then(res => console.log(res));
