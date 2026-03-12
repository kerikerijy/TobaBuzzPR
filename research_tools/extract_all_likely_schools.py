import re

def parse_mid_line(line):
    # Pattern: Name Num Num Num Num Ratio
    m = re.match(r'^([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
    if m:
        name = m.group(1).strip().replace(' ', '').replace('　', '')
        if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集"]): return None
        return {
            'name': name,
            'total': m.group(2),
            'early_quota': m.group(3),
            'mid_quota': m.group(4),
            'mid_app': m.group(5),
            'mid_rat': m.group(6)
        }
    return None

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

scraped = []
for line in lines:
    res = parse_mid_line(line.strip())
    if res:
        scraped.append(res)

# Also handle campus names in parentheses
for i, line in enumerate(lines):
    line = line.strip()
    m = re.match(r'^([（\(][^）\)]+[）\)])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
    if m:
        # Look back for parent school name if possible, but for now just take the campus name
        name = m.group(1).strip()
        scraped.append({
            'name': name,
            'total': m.group(2),
            'early_quota': m.group(3),
            'mid_quota': m.group(4),
            'mid_app': m.group(5),
            'mid_rat': m.group(6)
        })

# Sync with report to find missing
with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
    report_text = f.read()

print("Schools Found in PDF:")
for s in scraped:
    print(f"{s['name']}: Mid {s['mid_rat']} (App:{s['mid_app']}/Quota:{s['mid_quota']})")

print("\nMissing from Report:")
for s in scraped:
    if s['name'] not in report_text and s['name'].replace('（', '(').replace('）', ')') not in report_text:
        print(f"MISSING: {s['name']} | {s['mid_rat']}")

