# -*- coding: iso-8859-1 -*-
import io

index_path = r"public/index.html"

# Read file using iso-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    lines = f.readlines()

success = False
for idx, line in enumerate(lines):
    if "Mistura 2 a 3" in line and "tooltipSurpriseMe" in line:
        # Construct the new line using correct iso-8859-1 byte strings
        lines[idx] = '                tooltipSurpriseMe: "Mistura 2 a 3 raridades obscuras, cl\xe1ssicos de culto ou p\xe9rolas independentes aclamadas pela cr\xedtica com avalia\xe7\xf5es excelentes.",\n'
        success = True
        break

if success:
    with io.open(index_path, "w", encoding="iso-8859-1") as f:
        f.writelines(lines)
    print("Success: Updated Portuguese tooltip copy in dictionary via line index.")
else:
    print("Error: Portuguese line containing 'Mistura 2 a 3' not found.")
