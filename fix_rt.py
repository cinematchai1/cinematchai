import io

with io.open('public/index.html', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the corrupted '??' with the tomato emoji
code = code.replace(
    '<span class="text-xl leading-none">??</span>', 
    '<span class="text-xl leading-none">🍅</span>'
)

with io.open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed Rotten Tomatoes Emoji")
