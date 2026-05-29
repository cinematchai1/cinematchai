import io

index_path = r"C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\index.html"

# Read in ISO-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# Write in UTF-8
with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully converted index.html to UTF-8")
