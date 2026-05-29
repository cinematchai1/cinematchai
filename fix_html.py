import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix Broken Image Tags
html = html.replace('loading=" lazy\\ decoding=\\async\\ src=', 'loading="lazy" decoding="async" src=')
html = html.replace('loading=\\lazy\\ decoding=\\async\\ ', 'loading="lazy" decoding="async" ')

# 2. Fix Footer (Remove the global footer and put it in Terms/DMCA)
# Remove the injected footer
footer_pattern = re.compile(r'<!-- Legal Attribution Footer -->\s*<footer.*?</footer>', re.DOTALL)
html = footer_pattern.sub('', html)

# Add to PT terms
pt_terms_addition = r"<h4>6. Atribuição (APIs)</h4><p>Este produto utiliza a API do TMDB mas não é endossado nem certificado pelo TMDB. Dados adicionais fornecidos pela OMDb API (CC BY-NC 4.0) e Cinemeta.</p>"
html = html.replace('interrupções ou erros.</p>"', f'interrupções ou erros.</p>{pt_terms_addition}"')

# Add to EN terms
en_terms_addition = r"<h4>6. API Attribution</h4><p>This product uses the TMDB API but is not endorsed or certified by TMDB. Additional data provided by OMDb API (CC BY-NC 4.0) and Cinemeta.</p>"
html = html.replace('interruptions or errors.</p>"', f'interruptions or errors.</p>{en_terms_addition}"')

# 3. Fix Recommendation / Search Image sizes
# Ensure that all dynamically created images for movies have 'w-full h-full object-cover'
# Search for JS generated cards
html = html.replace("class=\"w-full h-full object-cover rounded-lg shadow-lg", "class=\"w-full h-full object-cover rounded-lg shadow-lg aspect-[2/3]")
html = html.replace("class=\"w-full h-full object-cover rounded-md shadow-lg", "class=\"w-full h-full object-cover rounded-md shadow-lg aspect-[2/3]")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML Fixed")
