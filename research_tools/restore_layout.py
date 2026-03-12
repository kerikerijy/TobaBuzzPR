import re

# 1. Read Original Structure (before breakage)
with open('/tmp/index_prev.html', 'r', encoding='utf-8') as f:
    orig_html = f.read()

# 2. Extract the Data Truth section (lines 234 to 1101 approx)
# We find the <section id="data-truth"> to <section id="landscape">
start_marker = '<section id="data-truth"'
end_marker = '<section id="landscape"'
start_idx = orig_html.find(start_marker)
end_idx = orig_html.find(end_marker)
data_truth_section = orig_html[start_idx:end_idx]

# 3. Read Current Broken Structure
with open('presentation/index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()

# 4. Replace the same section in current
curr_start = curr_html.find(start_marker)
curr_end = curr_html.find(end_marker)

if curr_start != -1 and curr_end != -1:
    new_html = curr_html[:curr_start] + data_truth_section + curr_html[curr_end:]
    with open('presentation/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Layout structure restored.")
else:
    print("Markers not found in current HTML.")
