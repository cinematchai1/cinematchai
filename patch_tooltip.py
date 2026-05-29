# -*- coding: iso-8859-1 -*-
import io

index_path = r"public/index.html"

# Read file using iso-8859-1
with io.open(index_path, "r", encoding="iso-8859-1") as f:
    content = f.read()

# 1. Replace the Surprise Me Label block with the label + tooltip HTML
target_html = '''                            <div class="flex flex-col gap-1.5 justify-center h-full pt-1">
                                <span id="lbl-surprise-me" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Surprise Me Mode</span>
                                <div class="flex items-center gap-3 mt-1.5">'''

replacement_html = '''                            <div class="flex flex-col gap-1.5 justify-center h-full pt-1">
                                <div class="flex items-center gap-1.5">
                                    <span id="lbl-surprise-me" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Surprise Me Mode</span>
                                    <div class="relative group flex items-center justify-center">
                                        <svg class="w-3.5 h-3.5 text-slate-500 hover:text-sky-400 transition-colors cursor-help" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 111.063.852l-.708 2.836a.75.75 0 001.063.852l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"/>
                                        </svg>
                                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 rounded bg-slate-900 border border-slate-700/80 shadow-2xl text-[10px] text-slate-300 font-normal leading-relaxed pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-50 text-center">
                                            <span id="tooltip-surprise-me">Mixes in 2-3 extremely obscure, highly-rated hidden indie gems or cult classics related to your search.</span>
                                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3 mt-1.5">'''

if target_html in content:
    content = content.replace(target_html, replacement_html)
    print("Success: Tooltip HTML inserted successfully.")
else:
    print("Error: Label target block not found.")

# 2. Add tooltip localization key for English ('en')
target_en = '''                lblSurpriseMe: "Surprise Me Mode",
                descSurpriseMe: "Mix in obscure hidden gems",'''

replacement_en = '''                lblSurpriseMe: "Surprise Me Mode",
                descSurpriseMe: "Mix in obscure hidden gems",
                tooltipSurpriseMe: "Mixes in 2-3 extremely obscure, highly-rated hidden indie gems or cult classics related to your search.",'''

if target_en in content:
    content = content.replace(target_en, replacement_en)
    print("Success: English tooltip dictionary key added.")
else:
    print("Error: English target keys not found.")

# 3. Add tooltip localization key for Portuguese ('pt')
target_pt = '''                lblSurpriseMe: "Modo Surpresa",
                descSurpriseMe: "Mistura raridades ocultas",'''

replacement_pt = '''                lblSurpriseMe: "Modo Surpresa",
                descSurpriseMe: "Mistura raridades ocultas",
                tooltipSurpriseMe: "Mistura 2 a 3 raridades obscuras, cl\xe1ssicos de culto ou p\xe9rolas independentes relacionadas com a pesquisa.",'''

if target_pt in content:
    content = content.replace(target_pt, replacement_pt)
    print("Success: Portuguese tooltip dictionary key added.")
else:
    print("Error: Portuguese target keys not found.")

# 4. Localize element in updateUI()
target_ui = '''            const descSurpriseMe = document.getElementById('desc-surprise-me');
            if (descSurpriseMe) descSurpriseMe.textContent = t.descSurpriseMe;'''

replacement_ui = '''            const descSurpriseMe = document.getElementById('desc-surprise-me');
            if (descSurpriseMe) descSurpriseMe.textContent = t.descSurpriseMe;
            const tooltipSurpriseMe = document.getElementById('tooltip-surprise-me');
            if (tooltipSurpriseMe) tooltipSurpriseMe.textContent = t.tooltipSurpriseMe;'''

if target_ui in content:
    content = content.replace(target_ui, replacement_ui)
    print("Success: updateUI tooltip assignment added.")
else:
    print("Error: updateUI target not found.")

# Write back using iso-8859-1
with io.open(index_path, "w", encoding="iso-8859-1") as f:
    f.write(content)

print("Tooltip integration finished.")
