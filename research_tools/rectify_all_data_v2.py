import re
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize(s):
    return s.strip().replace(' ', '').replace('　', '').replace('（', '(').replace('）', ')')

def get_mid_data(text):
    schools = {}
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Pattern 1: Basic school line
        # 京都八幡 160 66 94 2 0.02 160 70 5 0.07
        m = re.match(r'^([ぁ-んァ-ヶー一-龠\s\(\)（）]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m:
            name = normalize(m.group(1))
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集"]): continue
            if name not in schools:
                schools[name] = {'mid_quota': m.group(4), 'mid_app': m.group(5), 'mid_rat': m.group(6)}

        # Pattern 2: Multi-campus line (like Ayabe)
        # 綾　部 東 普通 40 - 40 4 0.10
        m2 = re.match(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+([ぁ-んァ-ヶー一-龠\s]+)\s+普通\s+40\s+-\s+40\s+(\d+)\s+([\d\.]+)', line)
        if m2:
            major = normalize(m2.group(1))
            campus = normalize(m2.group(2))
            name = f"{major}({campus})"
            schools[name] = {'mid_quota': '40', 'mid_app': m2.group(3), 'mid_rat': m2.group(4)}

    return schools

def get_early_data(text):
    early_data = {}
    lines = text.split('\n')
    current_major_school = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        # Identify possible school name
        if re.match(r'^[ぁ-んァ-ヶー一-龠][ぁ-んァ-ヶー一-龠\s　]{1,10}$', line):
            if not any(x in line for x in ["募集", "前期", "定員", "人数", "選抜", "方式", "合計"]):
                current_major_school = normalize(line)

        # Look for data row
        m = re.search(r'([ＡＢＣ]方式.*?)\s+(\d+\%)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m:
            etype = m.group(1).replace(' ', '')
            quota = m.group(3)
            app = m.group(4)
            rat = m.group(5)
            
            school_name = None
            name_on_line = re.match(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+\d+', line)
            if name_on_line:
                school_name = normalize(name_on_line.group(1))
            elif current_major_school:
                school_name = current_major_school
                
            if school_name:
                if school_name not in early_data: early_data[school_name] = []
                early_data[school_name].append({'type': etype, 'quota': quota, 'app': app, 'rat': rat})

    return early_data

MANUAL_FIXES = {
    "京都八幡": [
        {'type': 'Ａ方式', 'quota': '19', 'rat': '0.84'}
    ],
    "大江": [
        {'type': 'Ａ方式', 'quota': '63', 'rat': '0.57'}
    ],
    "綾部(東)": [
        {'type': 'Ａ方式', 'quota': '0', 'rat': '0.00'}
    ],
    "東舞鶴(浮島)": [
        {'type': 'Ａ方式', 'quota': '0', 'rat': '0.00'}
    ],
    "桂": [
         {'type': 'Ａ方式', 'quota': '84', 'rat': '5.31'}
    ]
}

def finalize():
    with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
        mid_text = f.read()
    with open('/tmp/kyoto8_early.txt', 'r', encoding='utf-8') as f:
        early_text = f.read()

    mid = get_mid_data(mid_text)
    early = get_early_data(early_text)

    # Apply fixes
    for k, v in MANUAL_FIXES.items():
        if k in early:
            for row in v:
                found = False
                for er in early[k]:
                    if er['type'] == row['type']:
                        er['quota'] = row['quota']
                        er['rat'] = row['rat']
                        found = True
                if not found:
                    early[k].append({'type': row['type'], 'quota': row['quota'], 'app': '', 'rat': row['rat']})
        else:
            early[k] = [{'type': row['type'], 'quota': row['quota'], 'app': '', 'rat': row['rat']} for row in v]

    # Combine names
    all_names = sorted(list(set(list(mid.keys()) + list(early.keys()))))
    
    def is_ordinary(name):
        exclude = ["商業", "工業", "農業", "園芸", "海洋", "音楽", "美術", "須知", "工学", "ものづくり", "まちづくり", "工学院", "奏和", "すばる", "人間科学"]
        if any(x in name for x in exclude): return False
        return True

    final_list = []
    for name in all_names:
        if not is_ordinary(name): continue
        m = mid.get(name, {'mid_quota': '-', 'mid_rat': '-'})
        # Special case for Ayabe(East) mid quota: it was 40 in regex
        e = early.get(name, [{'type': 'Ａ方式', 'quota': '-', 'rat': '-'}])
        final_list.append({'name': name, 'early': e, 'mid_q': m['mid_quota'], 'mid_r': m['mid_rat']})

    # Sort
    def mid_val(x):
        try: return float(x['mid_r'])
        except: return 0.0
    final_list.sort(key=mid_val, reverse=True)

    print("# 令和8年度 京都府公立高等学校 普通科志願倍率完全データ")
    print("| 学校名 | 【前期】方式 | 【前期】定員 | 【前期】倍率 | 【中期】定員 | 【中期】倍率 |")
    print("| :--- | :--- | :---: | :---: | :---: | :---: |")
    for s in final_list:
        if s['name'] == "計順位": continue
        e0 = s['early'][0]
        print(f"| {s['name']} | {e0.get('type','Ａ方式')} | {e0.get('quota','-')} | {e0.get('rat','-')} | {s['mid_q']} | {s['mid_r']} |")
        for sub in s['early'][1:]:
            print(f"| {s['name']} | {sub.get('type','Ａ方式')} | {sub.get('quota','-')} | {sub.get('rat','-')} | | |")

finalize()
