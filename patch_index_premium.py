# -*- coding: iso-8859-1 -*-
import io

index_path = r"public/index.html"

# Read file using iso-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# 1. Replace the settings drawer HTML (Right Section)
target_html = '''                    <!-- Right Section: Interactive App Customization -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center gap-2 pb-2 border-b border-slate-800/80">
                            <svg class="w-4 h-4 theme-accent-text" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122l9.37-9.37m0 0l-9.37-9.37M18.9 6.752H3.75"/></svg>
                            <h4 id="settings-custom-title" class="text-xs font-bold text-white uppercase tracking-wider text-slate-300">App Experience</h4>
                        </div>
                    </div>'''

replacement_html = '''                    <!-- Right Section: Discovery Focus Preferences -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center gap-2 pb-2 border-b border-slate-800/80">
                            <svg class="w-4 h-4 theme-accent-text" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122l9.37-9.37m0 0l-9.37-9.37M18.9 6.752H3.75"/></svg>
                            <h4 id="settings-custom-title" class="text-xs font-bold text-white uppercase tracking-wider text-slate-300">Discovery Focus</h4>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-content-type" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Content Focus</label>
                                <select id="filter-content-type" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white">
                                    <option value="any" id="opt-content-any">Mixed Content</option>
                                    <option value="movie" id="opt-content-movie">Movies Only</option>
                                    <option value="series" id="opt-content-series">TV Series Only</option>
                                </select>
                            </div>
                            <div class="flex flex-col gap-1.5 justify-center h-full pt-1">
                                <span id="lbl-surprise-me" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Surprise Me Mode</span>
                                <div class="flex items-center gap-3 mt-1.5">
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" id="filter-surprise-me" class="sr-only peer">
                                        <div class="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 peer-checked:after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500 theme-accent-bg"></div>
                                    </label>
                                    <span id="desc-surprise-me" class="text-[10px] text-slate-500 leading-none">Mix in obscure hidden gems</span>
                                </div>
                            </div>
                        </div>
                    </div>'''

if target_html in content:
    content = content.replace(target_html, replacement_html)
    print("Success: Replaced HTML layout.")
else:
    print("Error: Target HTML not found.")

# 2. Localize keys for English ('en')
target_en = '''                filterExcludeGenres: "Exclude Genres",
                filterExcludeGenresPlaceholder: "e.g. Horror, Documentary",
                settingsCustomTitle: "App Experience",'''

replacement_en = '''                filterExcludeGenres: "Exclude Genres",
                filterExcludeGenresPlaceholder: "e.g. Horror, Documentary",
                settingsCustomTitle: "Discovery Focus",
                lblContentType: "Content Focus",
                optContentAny: "Mixed Content",
                optContentMovie: "Movies Only",
                optContentSeries: "TV Series Only",
                lblSurpriseMe: "Surprise Me Mode",
                descSurpriseMe: "Mix in obscure hidden gems",'''

if target_en in content:
    content = content.replace(target_en, replacement_en)
    print("Success: English localization keys added.")
else:
    print("Error: English target keys not found.")

# 3. Localize keys for Portuguese ('pt')
target_pt = '''                filterExcludeGenres: "Excluir G\xe9neros",
                filterExcludeGenresPlaceholder: "ex: Terror, Document\xe1rio",
                settingsCustomTitle: "Experi\xeancia da App",'''

replacement_pt = '''                filterExcludeGenres: "Excluir G\xe9neros",
                filterExcludeGenresPlaceholder: "ex: Terror, Document\xe1rio",
                settingsCustomTitle: "Foco de Descoberta",
                lblContentType: "Foco do Conte\xfado",
                optContentAny: "Conte\xfado Misto",
                optContentMovie: "Apenas Filmes",
                optContentSeries: "Apenas S\xe9ries",
                lblSurpriseMe: "Modo Surpresa",
                descSurpriseMe: "Mistura raridades ocultas",'''

if target_pt in content:
    content = content.replace(target_pt, replacement_pt)
    print("Success: Portuguese localization keys added.")
else:
    # Try alternate encoding string
    target_pt_raw = '''                filterExcludeGenres: "Excluir Gêneros",
                filterExcludeGenresPlaceholder: "ex: Terror, Documentário",
                settingsCustomTitle: "Experiência da App",'''
    if target_pt_raw in content:
        content = content.replace(target_pt_raw, replacement_pt)
        print("Success: Portuguese raw localization keys added.")
    else:
        print("Error: Portuguese target keys not found.")

# 4. Add text localization updates in updateUI()
target_ui = '''            // App Customization elements localization
            const settingsCustomTitle = document.getElementById('settings-custom-title');
            if (settingsCustomTitle) settingsCustomTitle.textContent = t.settingsCustomTitle;'''

replacement_ui = '''            // App Customization elements localization
            const settingsCustomTitle = document.getElementById('settings-custom-title');
            if (settingsCustomTitle) settingsCustomTitle.textContent = t.settingsCustomTitle;
            const lblContentType = document.getElementById('lbl-content-type');
            if (lblContentType) lblContentType.textContent = t.lblContentType;
            const optContentAny = document.getElementById('opt-content-any');
            if (optContentAny) optContentAny.textContent = t.optContentAny;
            const optContentMovie = document.getElementById('opt-content-movie');
            if (optContentMovie) optContentMovie.textContent = t.optContentMovie;
            const optContentSeries = document.getElementById('opt-content-series');
            if (optContentSeries) optContentSeries.textContent = t.optContentSeries;
            const lblSurpriseMe = document.getElementById('lbl-surprise-me');
            if (lblSurpriseMe) lblSurpriseMe.textContent = t.lblSurpriseMe;
            const descSurpriseMe = document.getElementById('desc-surprise-me');
            if (descSurpriseMe) descSurpriseMe.textContent = t.descSurpriseMe;'''

if target_ui in content:
    content = content.replace(target_ui, replacement_ui)
    print("Success: updateUI text assignments added.")
else:
    print("Error: updateUI target not found.")

# 5. Extract filters defaultType and surpriseMe in performSearch()
target_search = '''            // Extract Filters
            const afterYear = document.getElementById('filter-year').value || '';
            const minRating = document.getElementById('filter-min-rating').value || '';
            const excludeGenres = document.getElementById('filter-exclude-genres').value || '';'''

replacement_search = '''            // Extract Filters
            const afterYear = document.getElementById('filter-year').value || '';
            const minRating = document.getElementById('filter-min-rating').value || '';
            const excludeGenres = document.getElementById('filter-exclude-genres').value || '';
            const defaultType = document.getElementById('filter-content-type').value || 'any';
            const surpriseMe = document.getElementById('filter-surprise-me').checked || false;'''

if target_search in content:
    content = content.replace(target_search, replacement_search)
    print("Success: Extract filters variables added.")
else:
    print("Error: Extract filters target not found.")

# 6. Add defaultType and surpriseMe to payload in performSearch()
target_payload = '''                const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData && lastMovieData.recommendations ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };'''

replacement_payload = '''                const payload = { 
                        movie, 
                        language: currentLang,
                        afterYear,
                        minRating,
                        excludeGenres,
                        defaultType,
                        surpriseMe,
                        limit: isLoadMore ? 10 : 5,
                        excludeTitles: isLoadMore ? (lastMovieData && lastMovieData.recommendations ? lastMovieData.recommendations.map(r => r.originalTitle || r.title) : []) : []
                    };'''

if target_payload in content:
    content = content.replace(target_payload, replacement_payload)
    print("Success: Payload properties added.")
else:
    print("Error: Payload target not found.")

# 7. Add defaultType and surpriseMe to local cache key to avoid cache collisions
target_cachekey = '''            // Local cache key using query filters to prevent collisions
            const cacheKey = `cinematch_cache_${movie.toLowerCase()}_${currentLang}_y:${afterYear}_r:${minRating}_e:${excludeGenres.toLowerCase().trim()}`;'''

replacement_cachekey = '''            // Local cache key using query filters to prevent collisions
            const cacheKey = `cinematch_cache_${movie.toLowerCase()}_${currentLang}_y:${afterYear}_r:${minRating}_e:${excludeGenres.toLowerCase().trim()}_t:${defaultType}_s:${surpriseMe}`;'''

if target_cachekey in content:
    content = content.replace(target_cachekey, replacement_cachekey)
    print("Success: CacheKey property added.")
else:
    print("Error: CacheKey target not found.")

# Write back using iso-8859-1
with io.open(index_path, "w", encoding="iso-8859-1") as f:
    f.write(content)

print("Premium settings drawer patch finished.")
