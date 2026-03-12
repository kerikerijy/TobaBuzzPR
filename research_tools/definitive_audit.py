import re

def extract_specialized(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    results = []
    current_school = None
    for i, line in enumerate(lines):
        line = line.strip()
        # School names are usually standalone or at start of section
        school_match = re.match(r'^([ぁ-んァ-ヶー一-龠]+)\s*$', line)
        if school_match:
            current_school = school_match.group(1)
        
        if "100%" in line:
            # Look back for course name
            course = "Unknown"
            if i > 0:
                prev = lines[i-1].strip()
                if not re.search(r'\d', prev):
                    course = prev
            
            # Extract numbers: Quota, Applicants, Ratio
            nums = re.findall(r'(\d+\.?\d*)', line)
            # Line format is tricky, but often: [TotalQuota, %, PartQuota, Applicants, Ratio]
            # Pattern: 120 A 方 式 100% 120 224 1.87
            if len(nums) >= 3:
                results.append({
                    "school": current_school,
                    "course": course,
                    "line": line,
                    "nums": nums
                })
    return results

def get_all_mid_schools():
    # We should extract this from the Mid-term text if possible
    # For now, let's just grep the Mid-term text for school names
    return []

early_specs = extract_specialized('/tmp/early_text.txt')
for s in early_specs:
    print(f"Spec Found: {s['school']} | {s['course']} | {s['line']}")
