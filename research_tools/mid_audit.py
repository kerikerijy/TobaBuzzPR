import re

with open('/tmp/mid_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

results = []
current_school = "Unknown"
for line in lines:
    # School names in Mid PDF usually look like "山　城" or "京都府立 山 城"
    # They often appear before the course data.
    # Let's try to find potential school names at the start of lines.
    school_match = re.match(r'^([ぁ-んァ-ヶー一-龠\s]{2,10})\s', line)
    if school_match:
        name = school_match.group(1).replace(" ", "").replace("　", "")
        if name and not re.search(r'\d', name):
            current_school = name

    if "普通" in line:
        nums = re.findall(r'(\d+\.?\d*)', line)
        if len(nums) >= 2:
            results.append({
                "school": current_school,
                "quota": nums[-3] if len(nums) >= 3 else "?",
                "ratio": nums[-1] if len(nums) >= 3 else "?"
            })

for r in results:
    print(f"Mid: {r['school']} | {r['quota']} | {r['ratio']}")
