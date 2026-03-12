import re
import os

def normalize(name):
    # Normalize brackets and remove spaces
    return name.replace(' ', '').replace('　', '').replace('（', '(').replace('）', ')')

# 1. Get all public schools from master data
public_schools = []
if os.path.exists('kyoto_highschool_data.md'):
    with open('kyoto_highschool_data.md', 'r', encoding='utf-8') as f:
        for line in f:
            if '| 京都府立' in line or '| 京都市立' in line:
                parts = line.split('|')
                if len(parts) > 1:
                    name = parts[1].strip()
                    # Remove prefix/suffix
                    name = name.replace('京都府立', '').replace('京都市立', '').replace('高等学校', '')
                    # Handle schools with middle school attached like "洛北高等学校・附属中学校"
                    if '・' in name:
                        name = name.split('・')[0]
                    public_schools.append(normalize(name))

print(f"DEBUG: Found {len(public_schools)} public schools in master data.")

# 2. Get schools already in report
report_schools = set()
if os.path.exists('kyoto_highschool_admission_ratios.md'):
    with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('|') and '学校名' not in line and '---' not in line:
                name = line.split('|')[1].strip()
                report_schools.add(normalize(name))

print(f"DEBUG: Found {len(report_schools)} schools in admission report.")

# 3. Check each public school in the Mid-term text
missing_candidates = []
if os.path.exists('/tmp/katsura_mid.txt'):
    with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
        mid_text = f.read()

    for school in public_schools:
        if school not in report_schools:
            # Flexible search (e.g., "京 都 八 幡")
            pattern = "".join([re.escape(c) + r"\s*" for c in school])
            if re.search(pattern, mid_text):
                missing_candidates.append(school)
            else:
                # Try partial match or alternate name if necessary
                # For now, let's just stick to exact matches of the base name
                pass

print("\nMissing Schools (Found in PDF but not in Report):")
for s in missing_candidates:
    print(f"- {s}")

