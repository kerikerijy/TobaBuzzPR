import re

def parse_mid(text):
    # Match patterns like:
    # 綾　部 180 54 126 110 0.87 180 126 145 1.15
    # 京都八幡 160 66 94 2 0.02 160 70 5 0.07
    # （加悦谷学舎） 80 22 58 37 0.64 80 56 27 0.48
    # 綾　部 東 普通 40 - 40 4 0.10 40 40 6 0.15
    
    results = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Try generic match
        # (Name/Campus) (Numbers...)
        m = re.match(r'^([ぁ-んァ-ヶー一-龠\s（）\(\)]+)\s+(\d+)\s+', line)
        if m:
            name = m.group(1).strip().replace(' ', '').replace('　', '')
            if any(x in name for x in ["合計", "選抜", "学校", "方式", "※", "学友", "学科", "募集"]): continue
            results.append(line)
            
    return results

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    text = f.read()

all_lines = parse_mid(text)
for l in all_lines:
    print(l)
