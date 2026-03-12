import re

def clean_name(name):
    if not name: return ""
    return name.replace(" ", "").replace("　", "").replace("京都府立", "").replace("京都市立", "").replace("高等学校", "")

def extract_early_specialized(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # We look for [School] [Course] ... [Quota] [100%]
    # This is hard because of PDF layout. Let's try splitting by school name.
    schools_raw = re.split(r'\n([ぁ-んァ-ヶー一-龠]{2,10})\s', text)
    results = []
    for i in range(1, len(schools_raw), 2):
        school = schools_raw[i].strip()
        content = schools_raw[i+1]
        
        # Look for 100% lines in content
        lines = content.split('\n')
        curr_course = "Unknown"
        for line in lines:
            if "100%" in line:
                nums = re.findall(r'(\d+\.?\d*)', line)
                if len(nums) >= 3:
                    # Try to find course name in prev lines
                    results.append({
                        "school": school,
                        "course": curr_course,
                        "line": line.strip(),
                        "quota": nums[-3] if len(nums) >= 3 else "?",
                        "applicants": nums[-2] if len(nums) >= 3 else "?",
                        "ratio": nums[-1] if len(nums) >= 3 else "?"
                    })
            else:
                # If a line has no numbers and is short, it might be a course name
                if not re.search(r'\d', line) and 2 <= len(line.strip()) <= 15:
                    curr_course = line.strip()
    return results

def extract_mid_ordinary(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Mid-term usually has "普通" courses.
    # We look for lines with "普通" and ratios.
    lines = text.split('\n')
    results = []
    current_school = "Unknown"
    for line in lines:
        school_match = re.match(r'^([ぁ-んァ-ヶー一-龠]{2,10})\s', line)
        if school_match:
            current_school = school_match.group(1).strip()
        
        if "普通" in line:
            nums = re.findall(r'(\d+\.?\d*)', line)
            if len(nums) >= 2:
                results.append({
                    "school": current_school,
                    "course": "普通",
                    "mid_quota": nums[-3] if len(nums) >= 3 else "?",
                    "mid_ratio": nums[-1] if len(nums) >= 3 else "?"
                })
    return results

print("--- Specialized (100% Early) ---")
specs = extract_early_specialized('/tmp/early_text.txt')
for s in specs:
    print(f"Spec: {s['school']} | {s['course']} | {s['quota']} | {s['ratio']}")

print("\n--- Ordinary (Mid) ---")
ords = extract_mid_ordinary('/tmp/mid_text.txt')
for o in ords:
    print(f"Ord: {o['school']} | {o['mid_quota']} | {o['mid_ratio']}")
