import re

def extract_schools(text):
    # This regex looks for: Name Number Number Number Number Number
    # We allow Name to have spaces.
    pattern = re.compile(r'([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', re.MULTILINE)
    matches = pattern.findall(text)
    schools = []
    for m in matches:
        name = m[0].strip().replace(' ', '').replace('　', '')
        if name and not any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科"]):
            schools.append(name)
    return sorted(list(set(schools)))

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    text = f.read()

found = extract_schools(text)
print("Schools Found in Mid-term PDF:")
for s in found:
    print(f"- {s}")

with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
    report = f.read()

missing = [s for s in found if s not in report]
print("\nMissing from Report:")
for s in missing:
    print(f"- {s}")
