import re

def parse_mid(text):
    results = []
    # This regex is more flexible. It looks for a name (optional campus) then numbers.
    # We'll parse line by line for better control.
    lines = text.split('\n')
    current_school = None
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Match school line: Name Total Early Mid App Ratio ...
        # Match pattern: 京都八幡 160 66 94 2 0.02
        m = re.match(r'^([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m:
            name = m.group(1).strip().replace(' ', '').replace('　', '')
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科"]): continue
            results.append({
                'name': name,
                'total': m.group(2),
                'early_quota': m.group(3),
                'mid_quota': m.group(4),
                'mid_app': m.group(5),
                'mid_rat': m.group(6)
            })
            continue
            
        # Match secondary campus lines: （加悦谷学舎） 80 22 58 37 0.64
        m2 = re.match(r'^([（\(][^）\)]+[）\)])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m2:
            name = m2.group(1).strip()
            results.append({
                'name': name,
                'total': m2.group(2),
                'early_quota': m2.group(3),
                'mid_quota': m2.group(4),
                'mid_app': m2.group(5),
                'mid_rat': m2.group(6)
            })
            continue

        # Match specific campus lines: 綾部 東 普通 40 - 40 4 0.10
        m3 = re.match(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+([ぁ-んァ-ヶー一-龠\s]+)\s+普通\s+40\s+-\s+40\s+(\d+)\s+([\d\.]+)', line)
        if m3:
            name = f"{m3.group(1).strip()}({m3.group(2).strip()})"
            results.append({
                'name': name.replace(' ', '').replace('　', ''),
                'total': '40',
                'early_quota': '0',
                'mid_quota': '40',
                'mid_app': m3.group(3),
                'mid_rat': m3.group(4)
            })

    return results

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    mid_text = f.read()

all_schools = parse_mid(mid_text)

# Filter for Ordinary Courses (mostly done by regex m3 or by checking report)
# We will just print everything we found that looks like a school and is missing.
with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
    report = f.read()

print("Parsed Schools (Missing from report):")
for s in all_schools:
    name = s['name']
    if name not in report and name.replace('（', '(').replace('）', ')') not in report:
        print(f"MISSING: {name} | MidRatio: {s['mid_rat']} | Quota: {s['mid_quota']}")

