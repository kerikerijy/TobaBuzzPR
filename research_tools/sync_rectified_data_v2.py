import re
import os

def generate_pill(name, early_data, mid_quota, mid_ratio, is_target=False):
    # Determine zone color (we'll just use the one from the container mostly, but for Toba we use blue)
    if is_target:
        return f"""
                                <div class="px-3 md:px-5 py-2 rounded-xl md:rounded-full bg-blue-600 border-2 border-blue-400 shadow-[0_0_20px_rgba(37,99,235,0.4)] flex items-center gap-3 cursor-pointer group relative scale-110 z-20">
                                    <div class="absolute -top-2 -right-2 bg-yellow-400 text-blue-900 text-[10px] font-black px-2 py-0.5 rounded-full shadow-lg animate-bounce">
                                        TARGET
                                    </div>
                                    <span class="text-white text-[13px] md:text-[14px] font-black tracking-tight flex items-center gap-1">
                                        鳥羽 <span class="text-[10px] font-medium opacity-80">普通科 ({mid_quota})</span>
                                    </span>
                                    <div class="flex items-center gap-1.5 font-mono text-[11px] md:text-[12px] whitespace-nowrap">
                                        <span class="text-blue-100 bg-blue-800/50 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-inner">
                                            <span class="text-[10px] opacity-70">前期({early_data[0]['q']})</span>{early_data[0]['r']}倍
                                        </span>
                                        <span class="text-white/40">→</span>
                                        <span class="text-white font-black bg-blue-900/60 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-lg border border-blue-400/30">
                                            <span class="text-[10px] opacity-70">中期({mid_quota})</span>{mid_ratio}倍
                                        </span>
                                    </div>
                                </div>"""
    else:
        # Standard Pill
        e_q = early_data[0]['q'] if early_data[0]['q'] != '-' else '-'
        e_r = early_data[0]['r'] if early_data[0]['r'] != '-' else '-'
        # Zone color logic (standard slate)
        return f"""
                                <div class="px-2 md:px-3 py-1.5 rounded-xl md:rounded-full bg-slate-800/80 border border-slate-700/50 hover:bg-slate-700 hover:border-slate-500 transition-all flex items-center gap-2 cursor-pointer group shadow-sm">
                                    <span class="text-slate-300 text-[12px] md:text-[13px]">{name}</span>
                                    <div class="flex items-center gap-1 font-mono text-[10px] md:text-[11px] whitespace-nowrap">
                                        <span class="text-slate-500 bg-slate-900/40 px-1.5 py-0.5 rounded flex items-center gap-1">
                                            <span class="text-[9px] opacity-60">前期({e_q})</span>{e_r}倍
                                        </span>
                                        <span class="text-slate-600">→</span>
                                        <span class="text-rose-400 font-bold bg-slate-900/60 px-1.5 py-0.5 rounded flex items-center gap-1">
                                            <span class="text-[9px] opacity-60">中期({mid_quota})</span>{mid_ratio}倍
                                        </span>
                                    </div>
                                </div>"""

def sync():
    # 1. Parse Markdown
    schools = []
    with open('kyoto_highschool_admission_ratios.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        current = None
        for line in lines:
            if '|' in line and '学校名' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 7:
                    name = parts[1]
                    if name:
                        current = {'name': name, 'early': [{'t':parts[2], 'q':parts[3], 'r':parts[4]}], 'mq':parts[5], 'mr':parts[6]}
                        schools.append(current)
                    elif current:
                        current['early'].append({'t':parts[2], 'q':parts[3], 'r':parts[4]})

    # 2. Group
    zones = {'S': [], 'A': [], 'B': [], 'C': []}
    for s in schools:
        try:
            r = float(s['mr'])
            if r > 1.20: zones['S'].append(s)
            elif r >= 1.10: zones['A'].append(s)
            elif r >= 1.00: zones['B'].append(s)
            else: zones['C'].append(s)
        except:
            zones['C'].append(s)

    with open('presentation/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 3. Surgical Replacement
    # For each zone, we find the container following the header.
    # Header pattern: ZONE X: .*? <span class="ml-auto text-slate-500">(\(\d+校\))</span>
    for z in ['S', 'A', 'B', 'C']:
        count = len(zones[z])
        # Update Count
        count_pattern = rf'ZONE {z}: .*?\n\s*<span class="ml-auto text-slate-500">\(\d+校\)</span>'
        replacement_header = f'ZONE {z}: {"高需要 (1.20倍超)" if z=="S" else "安定 (1.10倍〜)" if z=="A" else "定員充足 (1.00倍〜)" if z=="B" else "減少・定員割れ (1.00倍未満)"}\n                                <span class="ml-auto text-slate-500">({count}校)</span>'
        # html = re.sub(count_pattern, replacement_header, html)
        
        # Build Content
        content = ""
        for s in zones[z]:
            content += generate_pill(s['name'], s['early'], s['mq'], s['mr'], s['name'] == "鳥羽")
        
        # This is the tricky part: replace the pills within the <div> following the header.
        # We'll use a more targeted replacement by finding the header and then the NEXT <div class="flex flex-wrap ...">
        header_text = f"ZONE {z}:"
        pos = html.find(header_text)
        if pos != -1:
            # Update the count carefully
            count_section_start = html.find('(', pos)
            count_section_end = html.find(')', count_section_start)
            html = html[:count_section_start+1] + str(count) + "校" + html[count_section_end:]
            
            # Find the container
            container_start = html.find('<div class="flex flex-wrap', pos)
            if container_start != -1:
                inner_start = html.find('>', container_start) + 1
                # Find the end of this div
                # We count nested divs or just look for the next </div followed by another ZONE header or similar
                # For safety, we use a regex for the container ending
                next_zone_pos = html.find('ZONE ', inner_start)
                if next_zone_pos == -1: next_zone_pos = html.find('</section>', inner_start)
                
                div_end = html.rfind('</div>', inner_start, next_zone_pos)
                if div_end != -1:
                    html = html[:inner_start] + content + "\n                            " + html[div_end:]

    with open('presentation/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Sync complete.")

sync()
