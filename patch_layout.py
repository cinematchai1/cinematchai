# -*- coding: iso-8859-1 -*-
import io

index_path = r"public/index.html"

# Read file using iso-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# 1. Replace the Left Section (Advanced Filters) HTML layout (remove Exclude Genres, change to grid-cols-2, update placeholder, w-full, pr-8)
target_left_html = '''                    <!-- Left Section: AI Search Filters -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center gap-2 pb-2 border-b border-slate-800/80">
                            <svg class="w-4 h-4 theme-accent-text" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z"/></svg>
                            <h4 id="settings-title" class="text-xs font-bold text-white uppercase tracking-wider text-slate-300">Advanced Filters</h4>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-4">
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-min-rating" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Min IMDB Rating</label>
                                <select id="filter-min-rating" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white">
                                    <option value="all" id="opt-rating-all">All Ratings</option>
                                    <option value=">7.0">> 7.0</option>
                                    <option value=">8.0">> 8.0</option>
                                    <option value=">8.5">> 8.5</option>
                                </select>
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-year" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Year Limit (After)</label>
                                <input type="number" id="filter-year" placeholder="e.g. 2015" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white">
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-exclude-genres" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Exclude Genres</label>
                                <input type="text" id="filter-exclude-genres" placeholder="e.g. Horror, Documentary" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white">
                            </div>
                        </div>
                    </div>'''

replacement_left_html = '''                    <!-- Left Section: AI Search Filters -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center gap-2 pb-2 border-b border-slate-800/80">
                            <svg class="w-4 h-4 theme-accent-text" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z"/></svg>
                            <h4 id="settings-title" class="text-xs font-bold text-white uppercase tracking-wider text-slate-300">Advanced Filters</h4>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-min-rating" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Min IMDB Rating</label>
                                <select id="filter-min-rating" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white w-full min-w-[125px]">
                                    <option value="all" id="opt-rating-all">All Ratings</option>
                                    <option value=">7.0">> 7.0</option>
                                    <option value=">8.0">> 8.0</option>
                                    <option value=">8.5">> 8.5</option>
                                </select>
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label id="lbl-year" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Released After</label>
                                <input type="number" id="filter-year" placeholder="e.g. 2019" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white w-full">
                            </div>
                        </div>
                    </div>'''

if target_left_html in content:
    content = content.replace(target_left_html, replacement_left_html)
    print("Success: Replaced Left Section HTML layout.")
else:
    print("Error: Left Section HTML not found.")

# 2. Update Surprise Me Toggle Styling (Make active vs inactive states extremely obvious and gorgeous)
target_toggle = '''<div class="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 peer-checked:after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500 theme-accent-bg"></div>'''

replacement_toggle = '''<div class="w-9 h-5 bg-slate-950/70 border border-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-500 peer-checked:after:bg-white after:border-slate-600/40 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-sky-500 peer-checked:to-indigo-500 theme-accent-bg shadow-sm shadow-indigo-950/50"></div>'''

if target_toggle in content:
    content = content.replace(target_toggle, replacement_toggle)
    print("Success: Updated Surprise Me toggle styling.")
else:
    print("Error: Surprise Me toggle styling target not found.")

# 3. Update English Localization Dictionary
target_dict_en = '''                filterYear: "Year Limit (After)",
                filterExcludeGenres: "Exclude Genres",
                filterExcludeGenresPlaceholder: "e.g. Horror, Documentary",'''

replacement_dict_en = '''                filterYear: "Released After",'''

if target_dict_en in content:
    content = content.replace(target_dict_en, replacement_dict_en)
    print("Success: Updated English dictionary localization.")
else:
    print("Error: English dictionary target not found.")

# 4. Update Portuguese Localization Dictionary (use hex unicode escape to match properly)
# We will do line based replace since there are accents in PT dict
# Let's search line containing filterYear in PT
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    lines = f.readlines()

pt_success = False
for idx, line in enumerate(lines):
    if "filterYear:" in line and "Ano Limite" in line:
        lines[idx] = '                filterYear: "Lan\xe7ado Ap\xf3s",\n'
        pt_success = True

if pt_success:
    content = "".join(lines)
    print("Success: Updated Portuguese dictionary localization.")
else:
    print("Error: Portuguese dictionary line not found.")

# Write intermediate content to continue string checks
with io.open(index_path, "w", encoding="iso-8859-1") as f:
    f.write(content)

# Reload content
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# 5. Clean up updateUI() to remove Exclude Genres localization reference and use safe element verification
target_ui_exclude = '''            const lblExcludeGenres = document.getElementById('lbl-exclude-genres');
            if (lblExcludeGenres) lblExcludeGenres.textContent = t.filterExcludeGenres;
            const filterExcludeInput = document.getElementById('filter-exclude-genres');
            if (filterExcludeInput) filterExcludeInput.placeholder = t.filterExcludeGenresPlaceholder;'''

if target_ui_exclude in content:
    content = content.replace(target_ui_exclude, '')
    print("Success: Removed Exclude Genres from updateUI().")
else:
    print("Warning: Exclude Genres in updateUI() not found.")

# 6. Safe extract filter-exclude-genres to prevent TypeErrors in performSearch()
target_search = '''            const excludeGenres = document.getElementById('filter-exclude-genres').value || '';'''
replacement_search = '''            const excludeGenres = document.getElementById('filter-exclude-genres') ? document.getElementById('filter-exclude-genres').value : '';'''

if target_search in content:
    content = content.replace(target_search, replacement_search)
    print("Success: Patched performSearch() filter-exclude-genres extraction.")
else:
    print("Error: performSearch() filter-exclude-genres target not found.")

# Write back using iso-8859-1
with io.open(index_path, "w", encoding="iso-8859-1") as f:
    f.write(content)

print("Layout updates finished.")
