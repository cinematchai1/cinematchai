with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacements = [
    ("function openModal(type) {", "function openModal(type) {\n            document.body.style.overflow = 'hidden';"),
    ("function closeModal() {", "function closeModal() {\n            document.body.style.overflow = '';"),
    ("async function openProfileModal() {", "async function openProfileModal() {\n            document.body.style.overflow = 'hidden';"),
    ("function closeProfileModal() {", "function closeProfileModal() {\n            document.body.style.overflow = '';"),
    ("window.openDetailsModal = async function(b64) {", "window.openDetailsModal = async function(b64) {\n            document.body.style.overflow = 'hidden';"),
    ("window.closeDetailsModal = function() {", "window.closeDetailsModal = function() {\n            document.body.style.overflow = '';"),
    ("function openTrailer(ytId, title = '') {", "function openTrailer(ytId, title = '') {\n            document.body.style.overflow = 'hidden';"),
    ("function closeTrailer() {", "function closeTrailer() {\n            document.body.style.overflow = '';")
]

for old, new in replacements:
    html = html.replace(old, new)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched Modals Overflow")
