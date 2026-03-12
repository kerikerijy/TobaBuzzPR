import re

with open('presentation/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the double counts in headers
# Pattern like "ZONE S: 高需要 (1.20倍超) (9校)" -> we want just "ZONE S: 高需要 (1.20倍超)"
# because the span below has the "(9校)"
html = re.sub(r'(ZONE [SABC]: [^(\n]+) \(\d+校\)', r'\1', html)

# 2. Fix the summary section counts at the top (around lines 270-300)
# We need to find the stats cards at the top.
stats = {
    'S': 9,
    'A': 6,
    'B': 2,
    'C': 23
}

for z, count in stats.items():
    # Find the header "ZONE S: 超激戦 (2.0倍超)" or similar
    # And then update the (X校) in the following span
    pattern = rf'ZONE {z}: .*?\n\s*<span class="ml-auto text-slate-500">\(\d+校\)</span>'
    
    # We'll use a more direct string replacement for the stats cards
    # First search for the header text
    idx = html.find(f'ZONE {z}:')
    if idx != -1:
        span_idx = html.find('<span class="ml-auto text-slate-500">', idx)
        if span_idx != -1 and span_idx < idx + 200:
            c_start = html.find('(', span_idx)
            c_end = html.find(')', c_start)
            html = html[:c_start+1] + str(count) + "校" + html[c_end:]

with open('presentation/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Cleanup complete.")
