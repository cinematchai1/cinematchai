import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the grid columns from 3 to 2, and remove the Exclude Genres div block
target_grid_3 = '''                        <div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-4">
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
                        </div>'''

replacement_grid_2 = '''                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
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
                                <label id="lbl-year" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Released After</label>
                                <input type="number" id="filter-year" placeholder="e.g. 2019" class="bg-slate-900 border border-slate-700/60 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 theme-accent-ring text-white">
                            </div>
                        </div>'''

if target_grid_3 in content:
    content = content.replace(target_grid_3, replacement_grid_2)
    print("Success: Removed Exclude Genres from HTML layout and converted to 2-column grid.")
else:
    # Try with single or double quotes or minor variations
    print("Warning: Target HTML not matched exactly. Let's do a substring replacement.")
    # Fallback to direct replacement of the grid and the remove block
    if 'id="filter-exclude-genres"' in content:
        print("Found element id=filter-exclude-genres.")

# 2. Update English localization keys
target_en_keys = '''                filterMinRatingAll: "All Ratings",
                filterYear: "Year Limit (After)",
                filterExcludeGenres: "Exclude Genres",
                filterExcludeGenresPlaceholder: "e.g. Horror, Documentary",'''

replacement_en_keys = '''                filterMinRatingAll: "All Ratings",
                filterYear: "Released After",
                filterYearPlaceholder: "e.g. 2019",'''

if target_en_keys in content:
    content = content.replace(target_en_keys, replacement_en_keys)
    print("Success: English localization keys updated.")
else:
    print("Warning: English localization keys not found. Trying simpler match.")

# 3. Update Portuguese localization keys
target_pt_keys = '''                filterMinRatingAll: "Qualquer Nota",
                filterYear: "Lanço Após",'''

# Wait, let's check what the actual text is for pt filterYear:
# In the output it was: filterYear: "Lan\xe9ado Ap\xfas" or raw characters after converting to UTF-8
# Let's search and replace carefully.
# Let's do a direct replacement for the pt block
target_pt_part = 'filterMinRatingAll: "Qualque' # Let's see what the file actually has.

# Let's write a robust python search/replace for the pt dictionary:
import re
# We want to replace filterYear and filterExcludeGenres in the pt: { ... } block
content = re.sub(
    r'filterYear:\s*"[^"]*",\s*filterExcludeGenres:\s*"[^"]*",\s*filterExcludeGenresPlaceholder:\s*"[^"]*"',
    'filterYear: "Lançado Após",\n                filterYearPlaceholder: "ex: 2019"',
    content
)
print("Regex replacement run.")

# 4. Update updateUI() to apply placeholder dynamically
target_ui_code = '''            const lblYear = document.getElementById('lbl-year');
            if (lblYear) lblYear.textContent = t.filterYear;'''

replacement_ui_code = '''            const lblYear = document.getElementById('lbl-year');
            if (lblYear) lblYear.textContent = t.filterYear;
            const filterYear = document.getElementById('filter-year');
            if (filterYear) filterYear.placeholder = t.filterYearPlaceholder || 'e.g. 2019';'''

if target_ui_code in content:
    content = content.replace(target_ui_code, replacement_ui_code)
    print("Success: updateUI placeholder logic added.")
else:
    print("Warning: updateUI code not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished processing index.html updates.")
