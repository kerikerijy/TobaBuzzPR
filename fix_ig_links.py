import re

md_path = "kyoto_highschool_ig_data.md"

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <a href="URL" target="_blank">TEXT</a> with [TEXT](URL)
pattern = r'<a href="(.*?)"[^>]*>(.*?)</a>'
new_content = re.sub(pattern, r'[\2](\1)', content)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully converted HTML links to Markdown links.")
