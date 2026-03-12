import re
import os

def generate_card(name, early_data, mid_ratio, is_target=False):
    target_class = " target" if is_target else ""
    early_rows = ""
    for e in early_data:
        etype = e['type']
        erat = e['rat']
        early_rows += f'<div class="admission-row"><span>{etype}</span><span class="ratio">{erat}</span></div>'
    
    return f"""
                <div class="school-card{target_class}">
                    <div class="school-name">{name}</div>
                    <div class="admission-data">
                        <div class="admission-label">前期選抜倍率</div>
                        {early_rows}
                        <div class="admission-label">中期選抜倍率</div>
                        <div class="admission-row"><span>普通科</span><span class="ratio">{mid_ratio}</span></div>
                    </div>
                </div>"""

def sync():
    # 1. Parse Markdown
    schools = []
    with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        current_school = None
        for line in lines:
            if '|' in line and '学校名' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 7:
                    name = parts[1]
                    if name:
                        current_school = {
                            'name': name,
                            'early': [{'type': parts[2], 'rat': parts[4]}],
                            'mid_ratio': parts[6]
                        }
                        schools.append(current_school)
                    elif current_school:
                        # Sub row for early
                        current_school['early'].append({'type': parts[2], 'rat': parts[4]})

    # 2. Group into Zones
    zones = {'S': [], 'A': [], 'B': [], 'C': []}
    for s in schools:
        try:
            r = float(s['mid_ratio'])
            if r > 1.20: zones['S'].append(s)
            elif r >= 1.10: zones['A'].append(s)
            elif r >= 1.00: zones['B'].append(s)
            else: zones['C'].append(s)
        except:
            # Handle cases where mid_ratio is '-' (e.g. Katsura)
            zones['C'].append(s)

    # 3. Read index.html
    with open('presentation/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 4. Replace counts and blocks
    for zone in ['S', 'A', 'B', 'C']:
        count = len(zones[zone])
        # Replace count like "ZONE S: <span>(7校)</span>"
        html = re.sub(f'ZONE {zone}: <span>\(\d+校\)</span>', f'ZONE {zone}: <span>({count}校)</span>', html)
        
        # Build cards
        cards_html = ""
        for s in zones[zone]:
            cards_html += generate_card(s['name'], s['early'], s['mid_ratio'], s['name'] == "鳥羽")
        
        # Replace the grid content
        # Pattern: <!-- ZONE X START --> ... <!-- ZONE X END -->
        pattern = f'<!-- ZONE {zone} START -->.*?<!-- ZONE {zone} END -->'
        replacement = f'<!-- ZONE {zone} START -->{cards_html}\n                <!-- ZONE {zone} END -->'
        html = re.compile(pattern, re.DOTALL).sub(replacement, html)

    # 5. Write back
    with open('presentation/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Sync complete.")

sync()
