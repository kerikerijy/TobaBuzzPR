import re

def generate_pill(school_name, e_data, m_q, m_r, is_target=False):
    # e_data is a list of {'t': type, 'q': quota, 'r': ratio}
    
    # Format Early info
    early_parts = []
    for e in e_data:
        t_short = e['t'].replace('方式', '')
        early_parts.append(f'<span class="text-[9px] opacity-60">{t_short}({e["q"]})</span>{e["r"]}倍')
    
    early_html = ' <span class="text-slate-500">/</span> '.join(early_parts)
    
    if is_target:
        # Target (Toba) Style
        return f"""
                                <div class="px-3 md:px-5 py-2 rounded-xl md:rounded-full bg-blue-600 border-2 border-blue-400 shadow-[0_0_20px_rgba(37,99,235,0.4)] flex items-center gap-3 cursor-pointer group relative scale-110 z-20">
                                    <div class="absolute -top-2 -right-2 bg-yellow-400 text-blue-900 text-[10px] font-black px-2 py-0.5 rounded-full shadow-lg animate-bounce">
                                        TARGET
                                    </div>
                                    <span class="text-white text-[13px] md:text-[14px] font-black tracking-tight flex items-center gap-1">
                                        鳥羽 <span class="text-[10px] font-medium opacity-80">普通科 ({m_q})</span>
                                    </span>
                                    <div class="flex items-center gap-1.5 font-mono text-[11px] md:text-[12px] whitespace-nowrap">
                                        <div class="text-blue-100 bg-blue-800/50 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-inner">
                                            {early_html}
                                        </div>
                                        <span class="text-white/40">→</span>
                                        <span class="text-white font-black bg-blue-900/60 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-lg border border-blue-400/30">
                                            <span class="text-[10px] opacity-70">中期({m_q})</span>{m_r}倍
                                        </span>
                                    </div>
                                </div>"""
    else:
        # Standard Pill
        return f"""
                                <div class="px-2 md:px-3 py-1.5 rounded-xl md:rounded-full bg-slate-800/80 border border-slate-700/50 hover:bg-slate-700 hover:border-slate-500 transition-all flex items-center gap-2 cursor-pointer group shadow-sm">
                                    <span class="text-slate-300 text-[12px] md:text-[13px]">{school_name}</span>
                                    <div class="flex items-center gap-1 font-mono text-[10px] md:text-[11px] whitespace-nowrap">
                                        <span class="text-slate-500 bg-slate-900/40 px-1.5 py-0.5 rounded flex items-center gap-1">
                                            {early_html}
                                        </span>
                                        <span class="text-slate-600">→</span>
                                        <span class="text-rose-400 font-bold bg-slate-900/60 px-1.5 py-0.5 rounded flex items-center gap-1">
                                            <span class="text-[9px] opacity-60">中期({m_q})</span>{m_r}倍
                                        </span>
                                    </div>
                                </div>"""

def sync():
    # 1. Parse Report
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

    # 3. Read HTML
    with open('presentation/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 4. Find the "Ordinary Course" Column
    # It starts after <h3 class="...>...普通科の「真の需要」...</h3>
    col_start_marker = '普通科の「真の需要」'
    pos = html.find(col_start_marker)
    if pos == -1:
        print("Ordinary column marker not found.")
        return

    # Within this column, update ZONES
    for z in ['S', 'A', 'B', 'C']:
        z_header = f'ZONE {z}:'
        z_idx = html.find(z_header, pos)
        if z_idx != -1:
            # Update Count
            c_start = html.find('(', z_idx)
            c_end = html.find(')', c_start)
            count = len(zones[z])
            html = html[:c_start+1] + str(count) + "校" + html[c_end:]
            
            # Find the next flex-wrap container
            container_start = html.find('<div class="flex flex-wrap', z_idx)
            inner_start = html.find('>', container_start) + 1
            
            # Determine end of this zone's pills (before next ZONE or next Column/Section)
            next_z = html.find('ZONE ', inner_start)
            next_sect = html.find('<!-- Conclusion box -->', inner_start)
            if next_sect == -1: next_sect = html.find('</section>', inner_start)
            
            limit = next_z if next_z != -1 and (next_sect == -1 or next_z < next_sect) else next_sect
            div_end = html.rfind('</div>', inner_start, limit)
            
            # Generate Pills
            pills_html = ""
            for s in zones[z]:
                pills_html += generate_pill(s['name'], s['early'], s['mq'], s['mr'], s['name'] == "鳥羽")
            
            html = html[:inner_start] + pills_html + "\n                            " + html[div_end:]
            # Update current pos to after this replacement to continue correctly
            pos = html.find('ZONE ', inner_start) if next_z != -1 else limit

    with open('presentation/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Surgical sync complete.")

sync()
