import re

def get_mid_data(text):
    # This regex captures: Name Number Number Number Number Ratio
    # We'll be more aggressive here.
    pattern = re.compile(r'^([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', re.MULTILINE)
    matches = pattern.findall(text)
    schools = {}
    for m in matches:
        name = m[0].strip().replace(' ', '').replace('　', '').replace('（', '(').replace('）', ')')
        if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集"]): continue
        schools[name] = {
            'mid_quota': m[3],
            'mid_app': m[4],
            'mid_rat': m[5]
        }
    
    # Handle the "Ayabe East" style lines manually if needed
    # 綾部 東 普通 40 - 40 4 0.10
    special_pattern = re.compile(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+([ぁ-んァ-ヶー一-龠\s]+)\s+普通\s+40\s+-\s+40\s+(\d+)\s+([\d\.]+)', re.MULTILINE)
    for m in special_pattern.findall(text):
        name = f"{m[0].strip()}({m[1].strip()})".replace(' ', '').replace('　', '')
        schools[name] = {
            'mid_quota': '40',
            'mid_app': m[2],
            'mid_rat': m[3]
        }
    return schools

def get_early_data(text):
    # Early data is harder because it's multi-line.
    # We'll use a school names list to find corresponding lines.
    lines = text.split('\n')
    early_data = {}
    # Common A-method pattern: SchoolName ... Quota App Ratio
    for i, line in enumerate(lines):
        line = line.strip()
        # Look for the quota/app/ratio block which usually follows "Ａ方式" or "Ａ方式１型"
        if "Ａ方式" in line or "Ａ方式１型" in line or "Ａ方式２型" in line:
            # Look backwards for the school name (usually within 5 lines)
            school = None
            for j in range(i-1, max(0, i-6), -1):
                raw_name = lines[j].strip().replace(' ', '').replace('　', '')
                if raw_name and not any(x in raw_name for x in ["学科", "定員", "人数", "選抜"]):
                    school = raw_name
                    break
            
            if school:
                # Find the numbers in the current line or next lines
                # Pattern: Quota App Ratio (e.g. 24 125 5.21)
                nums = re.findall(r'(\d+)\s+(\d+)\s+([\d\.]+)', " ".join(lines[i:i+5]))
                if nums:
                    # Sort school name for matching
                    norm_school = school.replace('（', '(').replace('）', ')')
                    if norm_school not in early_data: early_data[norm_school] = []
                    early_data[norm_school].append({
                        'type': line,
                        'quota': nums[0][0],
                        'app': nums[0][1],
                        'rat': nums[0][2]
                    })
    return early_data

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    mid_text = f.read()
with open('/tmp/kyoto8_early.txt', 'r', encoding='utf-8') as f:
    early_text = f.read()

mid_schools = get_mid_data(mid_text)
early_schools = get_early_data(early_text)

# Merge
final_schools = []
all_names = sorted(list(set(list(mid_schools.keys()) + list(early_schools.keys()))))

for name in all_names:
    m = mid_schools.get(name, {'mid_quota':'', 'mid_app':'', 'mid_rat':''})
    e = early_schools.get(name, [])
    
    if not e:
        # Try finding early data by partial match (e.g. report "鳥羽" vs early "鳥羽" in multi-line)
        # But for now, let's keep it exact.
        row = {
            'name': name,
            'early': [{'type': 'Ａ方式', 'quota': '', 'app': '', 'rat': ''}],
            'mid_quota': m['mid_quota'],
            'mid_rat': m['mid_rat']
        }
        final_schools.append(row)
    else:
        # Multiple early lines (A1, A2)
        row = {
            'name': name,
            'early': e,
            'mid_quota': m['mid_quota'],
            'mid_rat': m['mid_rat']
        }
        final_schools.append(row)

# Filter for Ordinary Course entries only
# We exclude obvious experts: 農業, 工業, 商業, 園芸, 海洋
def is_ordinary(name):
    if is_target(name): return True
    exclude = ["農業", "工業", "商業", "園芸", "海洋", "音楽", "美術", "須知", "農芸", "工学院", "すばる", "奏和", "工学"]
    return not any(x in name for x in exclude)

def is_target(name):
    # Birds must stay
    return name in ["鳥羽", "城南菱創", "開建", "桂", "西舞鶴", "京都八幡", "大江", "綾部", "園部", "南丹", "丹後緑風"]

# Sort by mid_rat desc
def get_rat(s):
    try: return float(s['mid_rat'])
    except: return 0.0

final_filtered = [s for s in final_schools if is_ordinary(s['name'])]
final_filtered.sort(key=get_rat, reverse=True)

# Generate Markdown
print("# 令和8年度 京都府公立高等学校 普通科志願倍率完全データ")
print("| 学校名 | 【前期】方式 | 【前期】定員 | 【前期】倍率 | 【中期】定員 | 【中期】倍率 |")
print("| :--- | :--- | :---: | :---: | :---: | :---: |")

for s in final_filtered:
    # First row
    e1 = s['early'][0]
    print(f"| {s['name']} | {e1['type']} | {e1['quota']} | {e1['rat']} | {s['mid_quota']} | {s['mid_rat']} |")
    # Sub rows for early if exist
    for sub_e in s['early'][1:]:
        print(f"| {s['name']} | {sub_e['type']} | {sub_e['quota']} | {sub_e['rat']} | | |")

