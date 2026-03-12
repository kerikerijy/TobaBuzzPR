import re

with open('/tmp/early_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Look for patterns like "SchoolName CourseName Quota A/B/C-Method % Recruit Quota Applicant Ratio"
# Example: 自然科学 80 Ａ 方 式 100% 80 108 1.35
# Example: アカデミア 80 Ａ 方 式 100% 80 100 1.25

# We need to map school names to these courses.
# The PDF structure usually has the school name on the left and courses following it.

lines = text.split('\n')
specialized = []

# List of known specialized courses to track schools
keywords = [
    "自然科学", "人間科学", "アカデミア", "こすもす", "エンタープライジング", 
    "グローバル", "フロンティア", "教養", "サイエンス", "リサーチ", 
    "探究", "情報科学", "美術", "音楽", "スポーツ", "海洋", "農業", "園芸", "工業"
]

current_school = None
for line in lines:
    # Try to detect school name (usually 2-4 chars at start)
    # This is tricky in text extraction, but let's try
    school_match = re.match(r'^([ぁ-んァ-ヶー一-龠]{2,10})\s', line)
    if school_match:
        current_school = school_match.group(1).strip()
    
    for kw in keywords:
        if kw in line and "普通" not in line:
            # Try to extract numbers
            nums = re.findall(r'(\d+\.?\d*)', line)
            if len(nums) >= 3:
                # Often: [TotalQuota, %, Quota, Applicant, Ratio]
                specialized.append({
                    "school": current_school or "Unknown",
                    "course": kw,
                    "line": line.strip()
                })
                break

for item in specialized:
    print(f"{item['school']} | {item['course']} | {item['line']}")
