import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update performSearch renderMovies hasMoreResults check
target_show_btn = '''                // Show/hide the "Load More" button container based on hasMoreResults
                if (hasMoreResults) {
                    loadMoreContainer.classList.remove('hidden');
                    setTimeout(() => {
                        loadMoreContainer.style.opacity = '1';
                    }, 50);
                } else {
                    loadMoreContainer.classList.add('hidden');
                    loadMoreContainer.style.opacity = '0';
                }'''

replacement_show_btn = '''                // Show/hide the "Load More" button container based on hasMoreResults
                if (hasMoreResults) {
                    loadMoreContainer.classList.remove('hidden');
                    loadMoreContainer.classList.remove('hidden-section');
                    setTimeout(() => {
                        loadMoreContainer.style.opacity = '1';
                    }, 50);
                } else {
                    loadMoreContainer.classList.add('hidden');
                    loadMoreContainer.classList.add('hidden-section');
                    loadMoreContainer.style.opacity = '0';
                }'''

if target_show_btn in content:
    content = content.replace(target_show_btn, replacement_show_btn)
    print("Success: Patched performSearch renderMovies hasMoreResults visibility logic.")
else:
    print("Warning: target_show_btn not matched.")

# 2. Update renderMovies initial clean
target_render_init = '''            if (!isAppend) {
                resultsContainer.innerHTML = '';
                resultsContainer.style.opacity = '0';
                loadMoreContainer.classList.add('hidden');
                loadMoreContainer.style.opacity = '0';
            }'''

replacement_render_init = '''            if (!isAppend) {
                resultsContainer.innerHTML = '';
                resultsContainer.style.opacity = '0';
                loadMoreContainer.classList.add('hidden');
                loadMoreContainer.classList.add('hidden-section');
                loadMoreContainer.style.opacity = '0';
            }'''

if target_render_init in content:
    content = content.replace(target_render_init, replacement_render_init)
    print("Success: Patched renderMovies initial clean logic.")
else:
    print("Warning: target_render_init not matched.")

# 3. Update loadMore event listener when no more results
target_loadmore_end = '''                    if (!hasMoreResults) {
                        loadMoreContainer.classList.add('hidden');
                    }'''

replacement_loadmore_end = '''                    if (!hasMoreResults) {
                        loadMoreContainer.classList.add('hidden');
                        loadMoreContainer.classList.add('hidden-section');
                    }'''

if target_loadmore_end in content:
    content = content.replace(target_loadmore_end, replacement_loadmore_end)
    print("Success: Patched loadMore event listener final clean logic.")
else:
    print("Warning: target_loadmore_end not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished load more visibility patches.")
