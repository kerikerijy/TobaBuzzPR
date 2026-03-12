import re

def convert_md_to_html():
    with open('/Users/yamashita.jun.kk/Antigravity/TobaBuzzPR/kyoto_highschool_data.md', 'r') as f:
        lines = f.readlines()
    
    html_rows = []
    # Data rows start from line index 3 (4th line)
    for i, line in enumerate(lines[3:]):
        if not line.strip() or not line.startswith('|'): continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 7: continue
        
        name = parts[1]
        hp_match = re.search(r'\[公式HP\]\((.*?)\)', parts[2])
        hp_url = hp_match.group(1) if hp_match else ""
        
        ig_status = parts[3]
        ig_link = parts[4]
        followers = parts[5].replace(',', '')
        posts = parts[6]
        
        # Determine School Type
        school_type = "府立" # Default
        if "教育大学" in name: school_type = "国立"
        elif "市立" in name: school_type = "市立"
        elif "洛星" in name or "洛南" in name or "大谷" in name or "外大西" in name or "光華" in name or "国際" in name or "精華学園" in name or "成章" in name or "聖母" in name or "先端科学" in name or "橘" in name or "つくば開成" in name or "文教" in name or "美山" in name or "明徳" in name or "両洋" in name or "同志社" in name or "ノートルダム" in name or "花園" in name or "東山" in name or "平安女学院" in name or "洛陽総合" in name or "立命館" in name or "廣学館" in name or "聖カタリナ" in name or "共栄学園" in name or "成美" in name or "淑徳" in name or "日星" in name or "暁星" in name or "一燈園" in name or "華頂女子" in name or "翔英" in name or "西山" in name or "芸術" in name:
            school_type = "私立"
        
        ig_display = ""
        if "あり" in ig_status:
            ig_match = re.search(r'\[(.*?)\]\((.*?)\)', ig_link)
            if ig_match:
                tag = ig_match.group(1)
                url = ig_match.group(2)
                ig_display = f'<a href="{url}" target="_blank" style="color: var(--accent); text-decoration: none;">{tag} ↗</a>'
        else:
            ig_display = '<span style="color: #64748b;">未開設</span>'
            
        follower_val = followers if followers != "-" else "0"
        
        row = f"""                            <tr class="school-row" data-id="{i+1}" data-type="{school_type}" data-followers="{follower_val}"
                                style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <td style="padding: 1rem; color: #475569; font-family: monospace;">{i+1:03d}</td>
                                <td style="padding: 1rem; font-weight: 500;">{name}</td>
                                <td style="padding: 1rem;"><a href="{hp_url}"
                                        target="_blank" style="color: var(--primary); text-decoration: none;">公式サイト
                                        ↗</a> <span
                                        style="color: #475569; margin: 0 0.3rem; font-size: 0.8rem;">|</span> <a
                                        href="https://www.google.com/search?q={name}" target="_blank"
                                        style="color: #64748b; text-decoration: none; font-size: 0.85rem;">検索 ↗</a></td>
                                <td style="padding: 1rem;">{ig_display}</td>
                                <td style="padding: 1rem; text-align: right;">{parts[5]}</td>
                                <td style="padding: 1rem; text-align: right;">{parts[6]}</td>
                            </tr>"""
        html_rows.append(row)
    
    with open('/Users/yamashita.jun.kk/Antigravity/TobaBuzzPR/school_rows.html', 'w') as f:
        f.write('\n'.join(html_rows))

convert_md_to_html()
