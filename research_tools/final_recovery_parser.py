import re
import sys

def normalize(s):
    return s.strip().replace(' ', '').replace('　', '').replace('（', '(').replace('）', ')')

def get_flexible_pattern(name):
    # Matches "鳥羽" or "鳥　羽"
    return "".join([re.escape(c) + r"\s*" for c in name])

def parse_mid(text):
    schools = {}
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Basic: 京都八幡 160 66 94 2 0.02
        m = re.match(r'^([ぁ-んァ-ヶー一-龠\s\(\)（）]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)', line)
        if m:
            name = normalize(m.group(1))
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集", "計"]): continue
            if name not in schools:
                schools[name] = {'mq': m.group(4), 'mr': m.group(6)}
        
        # Campus: 綾部 東 普通 40 - 40 4 0.10
        m2 = re.match(r'^([ぁ-んァ-ヶー一-龠\s]+)\s+([ぁ-んァ-ヶー一-龠\s]+)\s+普通\s+40\s+-\s+40\s+(\d+)\s+([\d\.]+)', line)
        if m2:
            major = normalize(m2.group(1))
            campus = normalize(m2.group(2))
            name = f"{major}({campus})"
            schools[name] = {'mq': '40', 'mr': m2.group(4)}
    return schools

def parse_early(text, school_list):
    early_results = {}
    lines = text.split('\n')
    for school in school_list:
        # We handle "Ayabe(East)" as "Ayabe" anchor then look for "East" or just skip if known
        base_name = school.split('(')[0]
        pattern = get_flexible_pattern(base_name)
        
        found_school = False
        for i, line in enumerate(lines):
            if re.search(pattern, line.replace(' ', '').replace('　', '')):
                # Anchor found!
                # Now scan forward for selection rows
                for j in range(i, min(i+20, len(lines))):
                    l_sub = lines[j]
                    # Look for Quota App Ratio block
                    # Pattern: [etype] [quota] [app] [rat]
                    # Note: quota might be preceded by "30%" or similar
                    m = re.search(r'([ＡＢＣ]方式.*?)\s+(\d+\%|100\%)\s+(\d+)\s+(\d+)\s+([\d\.]+)', l_sub)
                    if m:
                        etype = m.group(1).replace(' ', '')
                        if school not in early_results: early_results[school] = []
                        early_results[school].append({'type': etype, 'quota': m.group(3), 'rat': m.group(5)})
                        found_school = True
                    # If we see another school-like name, stop
                    elif j > i and re.match(r'^[ぁ-んァ-ヶー一-龠]{2,5}$', l_sub.strip()) and not any(x in l_sub for x in ["方式", "募集"]):
                        break
                if found_school: break
    return early_results

def finalize():
    with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
        mid_text = f.read()
    with open('/tmp/kyoto8_early.txt', 'r', encoding='utf-8') as f:
        early_text = f.read()

    mid = parse_mid(mid_text)
    all_schools = sorted(list(mid.keys()))
    early = parse_early(early_text, all_schools)

    # Manual Cleanups/Overrides
    # Toba has A1 and A2
    early['鳥羽'] = [{'type': 'Ａ方式１型', 'quota': '24', 'rat': '5.13'}, {'type': 'Ａ方式２型', 'quota': '24', 'rat': '1.67'}]
    early['京都八幡'] = [{'type': 'Ａ方式', 'quota': '19', 'rat': '0.84'}]
    early['桂'] = [{'type': 'Ａ方式', 'quota': '84', 'rat': '5.31'}]
    early['鴨沂'] = [{'type': 'Ａ方式１型', 'quota': '48', 'rat': '5.17'}, {'type': 'Ａ方式２型', 'quota': '24', 'rat': '1.88'}]
    early['山城'] = [{'type': 'Ａ方式１型', 'quota': '48', 'rat': '4.98'}, {'type': 'Ａ方式２型', 'quota': '48', 'rat': '1.10'}]
    early['洛北'] = [{'type': 'Ａ方式１型', 'quota': '24', 'rat': '4.96'}, {'type': 'Ａ方式２型', 'quota': '24', 'rat': '1.17'}]
    early['乙訓'] = [{'type': 'Ａ方式１型', 'quota': '36', 'rat': '3.92'}, {'type': 'Ａ方式２型', 'quota': '24', 'rat': '1.50'}]

    # Filter for ordinary
    def is_ord(n):
        if n in ["鳥羽", "城南菱創", "開建", "桂", "西舞鶴", "京都八幡", "大江", "綾部", "園部", "南丹", "丹後緑風"]: return True
        exclude = ["商業", "工業", "農業", "園芸", "海洋", "音楽", "美術", "農芸", "須知", "工学院", "すばる", "奏和", "人間科学", "工学"]
        return not any(x in n for x in exclude)

    final = []
    for n in all_schools:
        if not is_ord(n): continue
        m_data = mid[n]
        e_data = early.get(n, [{'type': 'Ａ方式', 'quota': '-', 'rat': '-'}])
        final.append({'name': n, 'early': e_data, 'mid_q': m_data['mq'], 'mid_r': m_data['mr']})

    def get_mr(x):
        try: return float(x['mid_r'])
        except: return 0.0
    final.sort(key=get_mr, reverse=True)

    print("# 令和8年度 京都府公立高等学校 普通科志願倍率完全データ")
    print("| 学校名 | 【前期】方式 | 【前期】定員 | 【前期】倍率 | 【中期】定員 | 【中期】倍率 |")
    print("| :--- | :--- | :---: | :---: | :---: | :---: |")
    for s in final:
        e0 = s['early'][0]
        print(f"| {s['name']} | {e0['type']} | {e0['quota']} | {e0['rat']} | {s['mid_q']} | {s['mid_r']} |")
        for sub in s['early'][1:]:
            print(f"| {s['name']} | {sub['type']} | {sub['quota']} | {sub['rat']} | | |")

finalize()
