import json
import urllib.request
import urllib.parse
import time
import os
import ssl

DATA_FILE = "kyoto_highschool_data.md"
OUTPUT_FILE = "school_coordinates.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'TobaBuzzPR/1.0 (Contact: local-dev)'
}

def get_coordinates(school_name):
    query = f"京都府 {school_name}"
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and len(data) > 0:
                return {"lat": float(data[0]['lat']), "lng": float(data[0]['lon'])}
                
        # Retry with just school name if not found
        url2 = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(school_name)}&format=json&limit=1"
        req2 = urllib.request.Request(url2, headers=headers)
        with urllib.request.urlopen(req2, context=ctx) as response2:
            data2 = json.loads(response2.read().decode('utf-8'))
            if data2 and len(data2) > 0:
                return {"lat": float(data2[0]['lat']), "lng": float(data2[0]['lon'])}
                
        # Retry replacing 高等学校 with 高校
        if '高等学校' in school_name:
            short_query = f"{school_name.replace('高等学校', '高校')}"
            url3 = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(short_query)}&format=json&limit=1"
            req3 = urllib.request.Request(url3, headers=headers)
            with urllib.request.urlopen(req3, context=ctx) as response3:
                data3 = json.loads(response3.read().decode('utf-8'))
                if data3 and len(data3) > 0:
                    return {"lat": float(data3[0]['lat']), "lng": float(data3[0]['lon'])}

    except Exception as e:
        print(f"Error fetching {school_name}: {e}")
        
    return None

def main():
    schools = []
    
    if not os.path.exists(DATA_FILE):
        print(f"File not found: {DATA_FILE}")
        return
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines[3:]:
        if line.strip() == "":
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            school_name = parts[1]
            if school_name:
                schools.append(school_name)
            
    print(f"Loaded {len(schools)} schools. Starting geocoding...")
    
    results = {}
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"Loaded {len(results)} existing coordinates.")
        except json.JSONDecodeError:
            pass

    for i, school in enumerate(schools):
        if school in results:
            continue
            
        print(f"[{i+1}/{len(schools)}] Geocoding: {school}...", end="", flush=True)
        coords = get_coordinates(school)
        if coords:
            results[school] = coords
            print(f" -> Found: {coords}")
        else:
            print(" -> Not found.")
            
        time.sleep(1.5) # Nominatim policy: max 1 request per second
        
        if i % 5 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Done! Saved {len(results)}/{len(schools)} coordinates.")

if __name__ == "__main__":
    main()
