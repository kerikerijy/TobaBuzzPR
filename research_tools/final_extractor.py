import re

def get_mid_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split by schools (looking for names at beginning of lines or after punctuation)
    # Mid-term PDF has school names on the far left.
    lines = text.split('\n')
    results = []
    current_school = None
    
    for line in lines:
        line = line.strip()
        # School names often have spaces like "山　城"
        # We try to detect them at the start of a row
        school_match = re.search(r'^([ぁ-んァ-ヶー一-龠\s]{2,12})\s', line)
        if school_match:
            name = school_match.group(1).replace(" ", "").replace("　", "")
            # Basic validation for school name
            if len(name) >= 2 and not re.search(r'[0-9]', name) and name not in ["普通", "普通科", "専門学科", "募集人員"]:
                current_school = name

        if "普通" in line or "総合学科" in line:
            nums = re.findall(r'(\d+\.?\d*)', line)
            # Mid-term format: [Quota(A), Success(B), Remainder(C=A-B), Applicants(D), Ratio(D/C)]
            if len(nums) >= 3:
                results.append({
                    "school": current_school,
                    "course": "普通科" if "普通" in line else "総合学科",
                    "quota": nums[-3] if len(nums) >= 3 else "?",
                    "applicants": nums[-2] if len(nums) >= 3 else "?",
                    "ratio": nums[-1] if len(nums) >= 3 else "?"
                })
    return results

mid_ords = get_mid_data('/tmp/mid_text.txt')
print("--- ALL MID-TERM SCHOOLS ---")
seen = set()
for r in mid_ords:
    data = f"{r['school']} | {r['course']} | {r['quota']} | {r['ratio']}"
    if data not in seen:
        print(data)
        seen.add(data)
