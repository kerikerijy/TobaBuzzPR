import re

def parse_mid(text):
    # Pattern: Name Num Num Num Num Ratio
    # We skip names like "合計"
    pattern = re.compile(r'^([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', re.MULTILINE)
    matches = pattern.findall(text)
    schools = {}
    for m in matches:
        name = m[0].strip().replace(' ', '').replace('　', '')
        if not name or any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科"]): continue
        schools[name] = {
            'total': m[1],
            'rec': m[2],
            'mid_cap': m[3],
            'mid_app': m[4],
            'mid_rat': m[5]
        }
    return schools

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    text = f.read()

found = parse_mid(text)
print(f"Schools Found: {len(found)}")

with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
    report = f.read()

missing = []
for name in found:
    if name not in report and name.replace('（', '(').replace('）', ')') not in report:
        missing.append(name)

print("\nMissing from Report:")
for m in missing:
    print(f"| {m} | {found[m]['total']} | {found[m]['rec']} | {found[m]['mid_cap']} | {found[m]['mid_app']} | {found[m]['mid_rat']} |")
