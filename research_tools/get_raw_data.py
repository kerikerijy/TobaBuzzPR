import re

def find_data(text, school_pattern):
    lines = text.split('\n')
    for line in lines:
        if re.search(school_pattern, line.replace(' ', '').replace('　', '')):
            print(line)

with open('/tmp/katsura_mid.txt', 'r', encoding='utf-8') as f:
    mid = f.read()
with open('/tmp/kyoto8_early.txt', 'r', encoding='utf-8') as f:
    early = f.read()

schools = ["京都八幡", "大江", "綾部", "東舞鶴", "海洋", "桂", "鳥羽", "久御山"]

print("--- MID TERM RAW ---")
for s in schools:
    find_data(mid, s)

print("\n--- EARLY TERM RAW ---")
for s in schools:
    find_data(early, s)
