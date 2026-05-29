# -*- coding: iso-8859-1 -*-
import io

index_path = r"public/index.html"

# Read file using iso-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# Target for Load More visibility
target = '''            setTimeout(() => {
                referenceMovieContainer.style.opacity = '1';
                resultsContainer.style.opacity = '1';
            }, 50);'''

replacement = '''            setTimeout(() => {
                referenceMovieContainer.style.opacity = '1';
                resultsContainer.style.opacity = '1';
                
                // Show/hide the "Load More" button container based on hasMoreResults
                if (hasMoreResults) {
                    loadMoreContainer.classList.remove('hidden');
                    setTimeout(() => {
                        loadMoreContainer.style.opacity = '1';
                    }, 50);
                } else {
                    loadMoreContainer.classList.add('hidden');
                    loadMoreContainer.style.opacity = '0';
                }
            }, 50);'''

if target in content:
    content = content.replace(target, replacement)
    print("Success: Patched Load More visibility.")
else:
    print("Error: Target block for Load More visibility not found.")

# Write back using iso-8859-1
with io.open(index_path, "w", encoding="iso-8859-1") as f:
    f.write(content)

print("Patching finished.")
