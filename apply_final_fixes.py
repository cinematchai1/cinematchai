import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. HARDCODE BADGES CONTAINER
# Locate <div class="flex-grow mt-4 md:mt-0">
badges_html = '''
                        <h2 id="details-title" class="text-3xl md:text-5xl font-black text-white tracking-tight mb-2 leading-tight"></h2>
                        <div id="details-meta" class="flex flex-wrap items-center gap-3 text-slate-300 text-sm font-medium mb-4">
                            <span id="details-year" class="bg-slate-800 px-2 py-1 rounded text-sky-400"></span>
                            <span id="details-rating" class="border border-slate-600 px-2 py-1 rounded text-xs tracking-wider"></span>
                            <span id="details-runtime" class="flex items-center gap-1"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><span class="runtime-val"></span></span>
                            <span class="flex items-center gap-1 text-amber-400"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg><span id="details-rating-val"></span></span>
                        </div>
                        
                        <div id="details-badges" class="flex flex-wrap gap-3 mt-4 mb-4 items-center"></div>
'''

html = re.sub(
    r'<h2 id="details-title"[\s\S]*?<span id="details-rating-val"></span></span>\s*</div>',
    badges_html.strip(),
    html
)

# 2. FIX BADGES JS INJECTION
# Remove the old dynamic creation code
html = re.sub(
    r"const badgesContainer = document\.getElementById\('details-badges'\) \|\| document\.createElement\('div'\);\s*if \(\!document\.getElementById\('details-badges'\)\) \{\s*badgesContainer\.id = 'details-badges';\s*badgesContainer\.className = 'flex flex-wrap gap-3 mt-4 mb-4 items-center';\s*document\.getElementById\('details-buttons'\)\.parentNode\.insertBefore\(badgesContainer, document\.getElementById\('details-buttons'\)\);\s*\}",
    "const badgesContainer = document.getElementById('details-badges');",
    html
)

# 3. FIX LOAD MORE BUTTON TEXT & LOGIC
html = html.replace('Load 5 more suggestions', 'Discover More')

# Modify displayMovies logic
# Find: loadMoreContainer.classList.add('hidden');
# Replace with logic that only shows for results-grid
js_load_more = '''
        if (containerId === 'results-grid') {
            hasMoreResults = true; // Always allow fetching more from Gemini!
            loadMoreContainer.classList.remove('hidden');
            setTimeout(() => {
                loadMoreContainer.classList.remove('opacity-0');
            }, 100);
        } else {
            hasMoreResults = false;
            loadMoreContainer.classList.add('hidden');
            loadMoreContainer.classList.add('opacity-0');
        }
'''

html = re.sub(
    r"if \(\!hasMoreResults\) \{\s*loadMoreContainer\.classList\.add\('hidden'\);\s*\} else \{\s*loadMoreContainer\.classList\.remove\('hidden'\);\s*setTimeout\(\(\) => \{\s*loadMoreContainer\.classList\.remove\('opacity-0'\);\s*\}, 100\);\s*\}",
    js_load_more.strip(),
    html
)

# 4. UPDATE LEGAL TEXTS
terms_text = """
    <p class="mb-4">Welcome to our application. By using our service, you agree to these terms:</p>
    <ul class="list-disc pl-5 space-y-2 mb-4">
        <li><strong>Service Provision ("As-Is"):</strong> The service is provided on an "as-is" and "as available" basis. We do not warrant that the service will be uninterrupted, timely, secure, or error-free. We explicitly disclaim all warranties, express or implied.</li>
        <li><strong>External Links & APIs:</strong> This application relies on third-party APIs (such as TMDB, OMDb, and Cinemeta) to provide metadata, images, and ratings. We are not responsible for the accuracy, legality, or content provided by these external services.</li>
        <li><strong>Limitation of Liability:</strong> Under no circumstances shall the developers or owners of this site be liable for any direct, indirect, incidental, special, or consequential damages resulting from the use or inability to use the service.</li>
        <li><strong>Changes to Service:</strong> We reserve the right to modify, suspend, or discontinue the service at any time without prior notice.</li>
    </ul>
    <p class="text-sm text-slate-500 mt-6 border-t border-slate-700/50 pt-4">Data sources are attributed to their respective owners as required by their terms of use (e.g., TMDB, OMDb).</p>
"""
html = re.sub(r'<div id="content-terms" class="text-slate-300 text-sm leading-relaxed hidden">.*?</div>', f'<div id="content-terms" class="text-slate-300 text-sm leading-relaxed hidden">{terms_text}</div>', html, flags=re.DOTALL)

privacy_text = """
    <p class="mb-4">Your privacy is critically important to us.</p>
    <ul class="list-disc pl-5 space-y-2 mb-4">
        <li><strong>Data Collection:</strong> We collect non-personally identifiable information such as browser type, language preference, and referring site. We may also store session-based information necessary for user authentication and functionality (e.g., Watchlists).</li>
        <li><strong>Third-Party Processors:</strong> We use external services for data retrieval (TMDB, OMDb) and natural language processing (Google Gemini). When you perform a search, query data may be sent to these services.</li>
        <li><strong>Cookies:</strong> We use cookies strictly for maintaining user sessions and securing your access. We do not use tracking cookies for advertising.</li>
        <li><strong>Data Security:</strong> We implement standard security protocols to protect your data, but no method of transmission over the Internet is 100% secure.</li>
    </ul>
    <p class="text-sm text-slate-500 mt-6 border-t border-slate-700/50 pt-4">By continuing to use this service, you consent to this Privacy Policy.</p>
"""
html = re.sub(r'<div id="content-privacy" class="text-slate-300 text-sm leading-relaxed hidden">.*?</div>', f'<div id="content-privacy" class="text-slate-300 text-sm leading-relaxed hidden">{privacy_text}</div>', html, flags=re.DOTALL)

dmca_text = """
    <p class="mb-4">We respect the intellectual property rights of others. This application acts merely as a search engine and metadata aggregator.</p>
    <ul class="list-disc pl-5 space-y-2 mb-4">
        <li><strong>No Hosting of Copyrighted Media:</strong> We do not host, upload, or store any copyrighted video files, movies, or media streams on our servers. All metadata, posters, and trailers are provided via public APIs (TMDB, OMDb).</li>
        <li><strong>External Content:</strong> Any "Watch" or "Trailer" buttons link strictly to external platforms (like YouTube or third-party streaming aggregators). We have no control over the content hosted on these external websites.</li>
        <li><strong>Takedown Requests (DMCA):</strong> If you believe that your copyrighted work has been infringed upon by content displayed on our site, please contact the respective API providers (TMDB/OMDb) or the external hosts directly, as we do not control or host the data.</li>
    </ul>
    <p class="text-sm text-slate-500 mt-6 border-t border-slate-700/50 pt-4">This policy ensures compliance with the Digital Millennium Copyright Act (DMCA) Safe Harbor provisions.</p>
"""
html = re.sub(r'<div id="content-dmca" class="text-slate-300 text-sm leading-relaxed hidden">.*?</div>', f'<div id="content-dmca" class="text-slate-300 text-sm leading-relaxed hidden">{dmca_text}</div>', html, flags=re.DOTALL)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html patched with final fixes")
