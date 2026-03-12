import re
import sys

def normalize(s):
    return s.strip().replace(' ', '').replace('　', '').replace('（', '(').replace('）', ')')

def get_flexible_pattern(name):
    return "".join([re.escape(c) + r"\s*" for c in name])

def parse_mid(text):
    schools = {}
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        m = re.match(r'^([ぁ-んァ-ヶー一-龠\s\(\)（）]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m:
            name = normalize(m.group(1))
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集"]): continue
            schools[name] = {'mid_q': m.group(4), 'mid_r': m.group(6)}
        
        # Campus specific lines
        m2 = re.match(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+([ぁ-んァ-ヶー一-龠\s]+)\s+普通\s+40\s+-\s+40\s+(\d+)\s+([\d\.]+)', line)
        if m2:
            name = normalize(f"{m2.group(1)}({m2.group(2)})")
            schools[name] = {'mid_q': '40', 'mid_r': m2.group(4)}
    return schools

def parse_early(text, school_list):
    early_data = {}
    lines = text.split('\n')
    for school in school_list:
        pattern = get_flexible_pattern(school)
        for i, line in enumerate(lines):
            if re.search(pattern, line.replace(' ', '').replace('　', '')):
                # Found the school! Now look for A-method rows near it (within 10 lines)
                for j in range(i, min(i+15, len(lines))):
                    l_sub = lines[j]
                    m = re.search(r'([ＡＢＣ]方式.*?)\s+(\d+\%)\s+(\d+)\s+(\d+)\s+([\d\.]+)', l_sub)
                    if m:
                        etype = m.group(1).replace(' ', '')
                        if school not in early_data: early_data[school] = []
                        early_data[school].append({'type': etype, 'quota': m.group(3), 'rat': m.group(5)})
                if school in early_data: break
    return early_data

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    mid_text = f.read()
with open('/tmp/kyoto8_early.txt', 'r', encoding='utf-8') as f:
    early_text = f.read()

mid_schools = parse_mid(mid_text)
# We have 45 entries in current report, let's use them as a starting point + mid_schools
all_names = sorted(list(set(list(mid_schools.keys()))))
early_schools = parse_early(early_text, all_names)

# Manual Fixes for trickier ones
if '京都八幡' in all_names:
    early_schools['京都八幡'] = [{'type': 'Ａ方式', 'quota': '19', 'rat': '0.84'}]
if '桂' in all_names:
    early_schools['桂'] = [{'type': 'Ａ方式', 'quota': '84', 'rat': '5.31'}]

# Print final Table
print("# 令和8年度 京都府公立高等学校 普通科志願倍率完全データ")
print("| 学校名 | 【前期】方式 | 【前期】定員 | 【前期】倍率 | 【中期】定員 | 【中期】倍率 |")
print("| :--- | :--- | :---: | :---: | :---: | :---: |")

def is_ordinary(name):
    exclude = ["商業", "工業", "農業", "園芸", "海洋", "音楽", "美術", "須知", "工学", "ものづくり", "まちづくり", "工学院", "奏和", "すばる", "人間科学", "農芸"]
    return not any(x in name for x in exclude)

final_entries = []
for name in all_names:
    if not is_ordinary(name): continue
    m = mid_schools[name]
    e = early_schools.get(name, [{'type': 'Ａ方式', 'quota': '-', 'rat': '-'}])
    final_entries.append({'n': name, 'e': e, 'mq': m['mid_q'], 'mr': m['mid_r']})

def get_mr(x):
    try: return float(x['mr'])
    except: return 0.0

final_entries.sort(key=get_mr, reverse=True)

for s in final_entries:
    e0 = s['e'][0]
    print(f"| {s['n']} | {e0['type']} | {e0['quota']} | {e0['rat']} | {s['mq']} | {s['mr']} |")
    for ex in s['e'][1:]:
        print(f"| {s['n']} | {ex['type']} | {ex['quota']} | {ex['rat']} | | |")
