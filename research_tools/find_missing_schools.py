import re

def parse_mid(text):
    lines = text.split('\n')
    schools = {}
    for line in lines:
        parts = re.split(r'\s+', line.strip())
        if len(parts) >= 6:
            name = parts[0].replace(' ', '').replace('　', '')
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科"]): continue
            try:
                # Check for "京都八幡" especially
                total = int(parts[1])
                rec = int(parts[2])
                mid_cap = int(parts[3])
                mid_app = int(parts[4])
                mid_rat = parts[5]
                if total < 10: continue
                
                schools[name] = {
                    'total': total,
                    'rec': rec,
                    'mid_cap': mid_cap,
                    'mid_app': mid_app,
                    'mid_rat': mid_rat
                }
            except ValueError:
                continue
    return schools

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    mid_text = f.read()

mid_schools = parse_mid(mid_text)

with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
    report_text = f.read()

missing = []
for name in mid_schools:
    # Normalize name for matching
    norm_name = name.replace('（', '(').replace('）', ')')
    if name not in report_text and norm_name not in report_text:
        missing.append(name)

print(f"Total Schools Found in PDF: {len(mid_schools)}")
print("Missing Schools from Report:")
for m in missing:
    print(f"- {m}: {mid_schools[m]}")
