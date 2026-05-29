import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_modal_pattern = re.compile(r'window\.openDetailsModal = async function\(b64\)\s*\{.*?(?=window\.closeDetailsModal = function\(\)\s*\{)', re.DOTALL)

new_modal_code = """window.openDetailsModal = async function(b64) {
            let m;
            try { m = JSON.parse(decodeURIComponent(escape(atob(b64)))); } catch(e) { 
                try { m = JSON.parse(decodeURIComponent(atob(b64))); } catch(e2) { return; }
            }
            
            const title = m.name || m.title || '';
            const originalTitle = m.original_name || m.original_title || title;
            const year = m.year || m.releaseInfo || '';
            const type = m.type || 'movie';
            const imdbId = m.imdb_id || m.id || m.imdbId;
            
            const modal = document.getElementById('details-modal');
            const loading = document.getElementById('details-loading');
            const content = document.getElementById('details-content');
            
            modal.classList.remove('hidden');
            loading.classList.remove('hidden');
            content.classList.add('hidden');

            try {
                let finalData = null;

                if (imdbId && imdbId.startsWith('tt')) {
                    const res = await fetch(`/api/details/${type}/${imdbId}?lang=${currentLang}`);
                    if (res.ok) {
                        const data = await res.json();
                        finalData = data;
                    }
                }

                if (!finalData || !finalData.success) {
                    // Fallback to old proxy search if we don't have imdbId
                    const searchRes = await fetch(`/api/proxy/catalog/${type || 'movie'}/search=${encodeURIComponent(originalTitle || title)}`);
                    if (searchRes.ok) {
                        const searchData = await searchRes.json();
                        if (searchData.metas && searchData.metas.length > 0) {
                            const match = searchData.metas.find(m2 => m2.year == year) || searchData.metas[0];
                            const newImdbId = match.imdb_id || match.id;
                            if (newImdbId && newImdbId.startsWith('tt')) {
                                const res2 = await fetch(`/api/details/${type}/${newImdbId}?lang=${currentLang}`);
                                if (res2.ok) {
                                    finalData = await res2.json();
                                }
                            }
                        }
                    }
                }

                if (!finalData || !finalData.success) {
                    throw new Error("No data found");
                }

                const tmdb = finalData.tmdb;
                const omdb = finalData.omdb;
                const cinemeta = finalData.cinemeta;

                const displayTitle = tmdb ? (tmdb.title || tmdb.name) : (cinemeta ? cinemeta.name : title);
                const displayYear = tmdb ? (tmdb.release_date || tmdb.first_air_date || '').substring(0,4) : (cinemeta ? cinemeta.year : year);
                const displayPlot = tmdb && tmdb.overview ? tmdb.overview : (cinemeta ? cinemeta.description : 'No synopsis available.');
                
                document.getElementById('details-title').textContent = displayTitle;
                document.getElementById('details-year').textContent = displayYear;
                document.getElementById('details-type').textContent = (type === 'series' || type === 'tv') ? (currentLang === 'pt' ? 'Série' : 'Series') : (currentLang === 'pt' ? 'Filme' : 'Movie');
                document.getElementById('details-plot').textContent = displayPlot;
                
                let rtRating = 'N/A';
                let mcRating = 'N/A';
                let imdbRating = 'N/A';
                
                if (omdb && omdb.Ratings) {
                    const rt = omdb.Ratings.find(r => r.Source === 'Rotten Tomatoes');
                    if (rt) rtRating = rt.Value;
                    const mc = omdb.Ratings.find(r => r.Source === 'Metacritic');
                    if (mc) mcRating = mc.Value;
                }
                if (omdb && omdb.imdbRating) imdbRating = omdb.imdbRating;
                else if (tmdb && tmdb.vote_average) imdbRating = tmdb.vote_average.toFixed(1);
                else if (cinemeta && cinemeta.imdbRating) imdbRating = cinemeta.imdbRating;

                document.getElementById('details-rating-val').textContent = imdbRating;

                let duration = 'N/A';
                if (tmdb && tmdb.runtime) duration = tmdb.runtime + ' min';
                else if (cinemeta && cinemeta.runtime) duration = cinemeta.runtime;
                document.getElementById('details-duration').textContent = duration;
                
                const posterEl = document.getElementById('details-poster');
                const bgEl = document.getElementById('details-bg');
                
                let posterUrl = tmdb && tmdb.poster_path ? `https://image.tmdb.org/t/p/w500${tmdb.poster_path}` : (cinemeta ? cinemeta.poster : '');
                posterEl.src = posterUrl;
                
                let bgUrl = tmdb && tmdb.backdrop_path ? `https://image.tmdb.org/t/p/w1280${tmdb.backdrop_path}` : (cinemeta && cinemeta.background ? cinemeta.background : posterUrl);
                bgEl.style.backgroundImage = `url('${bgUrl}')`;

                document.getElementById('details-director').textContent = omdb && omdb.Director && omdb.Director !== 'N/A' ? omdb.Director : (cinemeta && cinemeta.director ? cinemeta.director.join(', ') : 'N/A');
                const castContainer = document.getElementById('details-cast');
                castContainer.innerHTML = '';
                
                let castList = [];
                if (tmdb && tmdb.credits && tmdb.credits.cast) castList = tmdb.credits.cast.slice(0, 5).map(c => c.name);
                else if (cinemeta && cinemeta.cast) castList = cinemeta.cast.slice(0, 5);
                else if (omdb && omdb.Actors && omdb.Actors !== 'N/A') castList = omdb.Actors.split(',').slice(0, 5).map(s => s.trim());

                if (castList.length > 0) {
                    castList.forEach(c => {
                        const p = document.createElement('p');
                        p.textContent = c;
                        castContainer.appendChild(p);
                    });
                } else {
                    castContainer.textContent = 'N/A';
                }

                const genresContainer = document.getElementById('details-genres');
                genresContainer.innerHTML = '';
                let genresList = [];
                if (tmdb && tmdb.genres) genresList = tmdb.genres.map(g => g.name);
                else if (cinemeta && cinemeta.genre) genresList = cinemeta.genre;
                else if (omdb && omdb.Genre && omdb.Genre !== 'N/A') genresList = omdb.Genre.split(',').map(g => g.trim());

                genresList.forEach(g => {
                    const span = document.createElement('span');
                    span.className = 'px-2 py-0.5 rounded text-xs font-medium bg-slate-800/80 border border-slate-700/50 text-slate-300';
                    span.textContent = g;
                    genresContainer.appendChild(span);
                });

                const badgesContainer = document.getElementById('details-badges') || document.createElement('div');
                if (!document.getElementById('details-badges')) {
                    badgesContainer.id = 'details-badges';
                    badgesContainer.className = 'flex flex-wrap gap-3 mt-4 mb-4 items-center';
                    document.getElementById('details-buttons').parentNode.insertBefore(badgesContainer, document.getElementById('details-buttons'));
                }
                badgesContainer.innerHTML = '';
                
                if (rtRating !== 'N/A') {
                    badgesContainer.innerHTML += `<div class="flex items-center gap-1 bg-rose-500/20 px-2 py-1 rounded text-rose-400 font-bold text-sm border border-rose-500/30"><span class="text-xl leading-none">🍅</span> ${rtRating}</div>`;
                }
                if (mcRating !== 'N/A') {
                    badgesContainer.innerHTML += `<div class="flex items-center gap-1 bg-green-500/20 px-2 py-1 rounded text-green-400 font-bold text-sm border border-green-500/30"><span class="text-xl leading-none font-black tracking-tighter">M</span> ${mcRating}</div>`;
                }
                if (imdbRating !== 'N/A') {
                    badgesContainer.innerHTML += `<div class="flex items-center gap-1 bg-amber-500/20 px-2 py-1 rounded text-amber-400 font-bold text-sm border border-amber-500/30"><span class="text-xl leading-none font-black tracking-tighter">IMDb</span> ${imdbRating}</div>`;
                }

                const btnsContainer = document.getElementById('details-buttons');
                btnsContainer.innerHTML = '';
                
                let ytTrailer = null;
                if (tmdb && tmdb.videos && tmdb.videos.results) {
                    const trailer = tmdb.videos.results.find(v => v.type === 'Trailer' && v.site === 'YouTube') || tmdb.videos.results[0];
                    if (trailer) ytTrailer = trailer.key;
                } else if (cinemeta && cinemeta.trailers && cinemeta.trailers.length > 0) {
                    ytTrailer = cinemeta.trailers[0].source;
                }
                
                if (ytTrailer) {
                    btnsContainer.innerHTML += `
                        <button onclick="openTrailer('${ytTrailer}', '${displayTitle.replace(/'/g, "\\'")}')" class="bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold py-2.5 px-6 rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-amber-500/20">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Trailer
                        </button>
                    `;
                }
                
                const resolvedTmdbId = tmdb ? tmdb.id : (cinemeta ? cinemeta.moviedb_id : m.tmdbId);
                const urlType = (type === 'series' || type === 'tv') ? 'tv' : 'movie';
                const slug = displayTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
                const watchUrl = resolvedTmdbId 
                    ? `https://flixmomo.app/${urlType}/${resolvedTmdbId}/${slug}` 
                    : `https://flixmomo.app/search?q=${encodeURIComponent(displayTitle)}`;
                
                btnsContainer.innerHTML += `
                    <a href="${watchUrl}" target="_blank" class="bg-sky-600 hover:bg-sky-500 text-white font-bold py-2.5 px-6 rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-sky-600/20">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg> Watch Now
                    </a>
                `;

            } catch (err) {
                console.error("Details Modal Error:", err);
            } finally {
                loading.classList.add('hidden');
                content.classList.remove('hidden');
            }
        }

        """

new_content = old_modal_pattern.sub(new_modal_code, content)
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated index.html successfully")
