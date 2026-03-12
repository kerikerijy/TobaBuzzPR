import json
import re

md_path = "kyoto_highschool_ig_data.md"
json_path = "hp_research_data_exported.json"

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {json_path} not found.")
    exit(1)

# Create a mapping of school name to HP URL
url_map = {item['name']: item['official_hp_url'] for item in data}

try:
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {md_path} not found.")
    exit(1)

new_lines = []
for line in lines:
    if line.strip().startswith('|'):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 6:
            if '学校名' in line:
                # Header row
                parts.insert(2, "公式HP URL")
                new_line = '| ' + ' | '.join(parts[1:-1]) + ' |\n'
                new_lines.append(new_line)
            elif '---' in line:
                # Separator row
                parts.insert(2, "---")
                new_line = '| ' + ' | '.join(parts[1:-1]) + ' |\n'
                new_lines.append(new_line)
            else:
                # Data row
                name_html = parts[1]
                name = re.sub(r'<[^>]+>', '', name_html).strip()
                
                hp_url = url_map.get(name, '')
                hp_md = f"[公式HP]({hp_url})" if hp_url else "-"
                
                parts.insert(2, hp_md)
                new_line = '| ' + ' | '.join(parts[1:-1]) + ' |\n'
                new_lines.append(new_line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully updated {md_path} with Official HP URLs.")
