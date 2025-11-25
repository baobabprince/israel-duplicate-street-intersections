#!/usr/bin/env python3
import sys
import json
import csv
import requests
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371000

def get_city_data(city_name):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    area["name"="{city_name}"]["admin_level"~"^(7|8)$"]["boundary"="administrative"]->.city;
    (
      way(area.city)["highway"]["name"];
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.post(overpass_url, data={"data": query})
    return response.json()

def are_similar_names(name1, name2):
    """Check if two street names are essentially the same (just different order/spelling)"""
    # Normalize: lowercase, remove common prefixes/suffixes, split to words
    def normalize(name):
        name = name.lower()
        # Remove common prefixes
        for prefix in ['רחוב ', 'שדרות ', 'דרך ', 'רח\' ', 'שד\' ']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        return set(name.split())
    
    words1 = normalize(name1)
    words2 = normalize(name2)
    
    # If one set is subset of the other, they're similar
    if words1.issubset(words2) or words2.issubset(words1):
        return True
    
    # If they share most words (>70%), they're similar
    if len(words1) > 0 and len(words2) > 0:
        common = len(words1 & words2)
        similarity = common / max(len(words1), len(words2))
        if similarity > 0.7:
            return True
    
    return False

def find_duplicate_intersections(city_name, min_distance=150, max_distance=None):
    print(f"מוריד נתונים עבור {city_name}...")
    data = get_city_data(city_name)
    
    nodes = {e['id']: (e['lon'], e['lat']) for e in data['elements'] if e['type'] == 'node'}
    ways = [e for e in data['elements'] if e['type'] == 'way' and 'name' in e.get('tags', {})]
    
    node_to_streets = defaultdict(set)
    for way in ways:
        street_name = way['tags']['name']
        for node_id in way['nodes']:
            if node_id in nodes:
                node_to_streets[node_id].add(street_name)
    
    street_pairs = defaultdict(list)
    for node_id, streets in node_to_streets.items():
        if len(streets) >= 2:
            for s1 in streets:
                for s2 in streets:
                    if s1 < s2:
                        pair = (s1, s2)
                        street_pairs[pair].append(nodes[node_id])
    
    results = []
    seen_pairs = {}  # Track street pairs and keep only the one with max distance
    
    for (street1, street2), locations in street_pairs.items():
        # Skip if street names are too similar (likely same street with inconsistent naming)
        if are_similar_names(street1, street2):
            continue
            
        if len(locations) >= 2:
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    lon1, lat1 = locations[i]
                    lon2, lat2 = locations[j]
                    distance = haversine(lon1, lat1, lon2, lat2)
                    if distance >= min_distance and (max_distance is None or distance <= max_distance):
                        pair_key = (street1, street2)
                        # Keep only the intersection with maximum distance for each street pair
                        if pair_key not in seen_pairs or distance > seen_pairs[pair_key]['distance']:
                            seen_pairs[pair_key] = {
                                'street1': street1,
                                'street2': street2,
                                'distance': distance,
                                'location1': (lat1, lon1),
                                'location2': (lat2, lon2)
                            }
    
    results = list(seen_pairs.values())
    return results

def export_to_csv(results, city_name):
    filename = f"{city_name}_intersections.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['רחוב 1', 'רחוב 2', 'מרחק (מטר)', 'קו רוחב 1', 'קו אורך 1', 'קו רוחב 2', 'קו אורך 2'])
        for r in results:
            writer.writerow([r['street1'], r['street2'], f"{r['distance']:.0f}", 
                           r['location1'][0], r['location1'][1], r['location2'][0], r['location2'][1]])
    print(f"✓ נשמר ל-{filename}")

def export_to_json(results, city_name):
    filename = f"{city_name}_intersections.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ נשמר ל-{filename}")

def export_to_html(results, city_name):
    filename = f"{city_name}_intersections.html"
    center_lat = sum(r['location1'][0] + r['location2'][0] for r in results) / (2 * len(results))
    center_lon = sum(r['location1'][1] + r['location2'][1] for r in results) / (2 * len(results))
    
    markers_data = []
    for i, r in enumerate(results, 1):
        markers_data.append({
            'num': i,
            'street1': r['street1'],
            'street2': r['street2'],
            'distance': f"{r['distance']:.0f}",
            'lat1': r['location1'][0],
            'lon1': r['location1'][1],
            'lat2': r['location2'][0],
            'lon2': r['location2'][1]
        })
    
    html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="utf-8">
    <title>מפגשי רחובות כפולים - {city_name}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; }}
        #info {{ padding: 20px; background: #2c3e50; color: white; }}
        h1 {{ margin: 0 0 10px 0; }}
        .stats {{ color: #ecf0f1; }}
        #container {{ display: flex; height: calc(100vh - 80px); }}
        #list {{ width: 400px; overflow-y: auto; background: #f5f5f5; border-left: 2px solid #ccc; }}
        #map {{ flex: 1; }}
        .item {{ padding: 15px; border-bottom: 1px solid #ddd; cursor: pointer; transition: background 0.2s; }}
        .item:hover {{ background: #e8e8e8; }}
        .item.active {{ background: #3498db; color: white; }}
        .item-num {{ font-weight: bold; color: #e74c3c; }}
        .item.active .item-num {{ color: white; }}
        .item-streets {{ font-size: 14px; margin: 5px 0; }}
        .item-distance {{ font-size: 12px; color: #666; }}
        .item.active .item-distance {{ color: #ecf0f1; }}
    </style>
</head>
<body>
    <div id="info">
        <h1>מפגשי רחובות כפולים ב{city_name}</h1>
        <p class="stats">נמצאו {len(results)} תוצאות | לחץ על תוצאה כדי להתמקד במפה</p>
    </div>
    <div id="container">
        <div id="list"></div>
        <div id="map"></div>
    </div>
    <script>
        const data = {json.dumps(markers_data, ensure_ascii=False)};
        
        const map = L.map('map').setView([{center_lat}, {center_lon}], 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap'
        }}).addTo(map);
        
        const markers = {{}};
        const lines = {{}};
        
        data.forEach(item => {{
            const m1 = L.marker([item.lat1, item.lon1]).addTo(map)
                .bindPopup(`<b>#${{item.num}}</b><br>${{item.street1}} ⚬ ${{item.street2}}<br>מיקום 1<br>מרחק: ${{item.distance}}m`);
            const m2 = L.marker([item.lat2, item.lon2]).addTo(map)
                .bindPopup(`<b>#${{item.num}}</b><br>${{item.street1}} ⚬ ${{item.street2}}<br>מיקום 2<br>מרחק: ${{item.distance}}m`);
            const line = L.polyline([[item.lat1, item.lon1], [item.lat2, item.lon2]], 
                {{color: 'red', weight: 2, opacity: 0.5}}).addTo(map);
            
            markers[item.num] = [m1, m2];
            lines[item.num] = line;
        }});
        
        const list = document.getElementById('list');
        data.forEach(item => {{
            const div = document.createElement('div');
            div.className = 'item';
            div.innerHTML = `
                <div class="item-num">#${{item.num}}</div>
                <div class="item-streets">${{item.street1}} ⚬ ${{item.street2}}</div>
                <div class="item-distance">מרחק: ${{item.distance}} מטר</div>
            `;
            div.onclick = () => {{
                document.querySelectorAll('.item').forEach(el => el.classList.remove('active'));
                div.classList.add('active');
                const midLat = (item.lat1 + item.lat2) / 2;
                const midLon = (item.lon1 + item.lon2) / 2;
                map.setView([midLat, midLon], 16);
                markers[item.num][0].openPopup();
            }};
            list.appendChild(div);
        }});
    </script>
</body>
</html>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ נשמר ל-{filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("שימוש: python find_duplicate_intersections.py <שם_עיר> [מרחק_מינימלי] [מרחק_מקסימלי]")
        print("דוגמה: python find_duplicate_intersections.py ירושלים 150 1000")
        sys.exit(1)
    
    city_name = sys.argv[1]
    min_dist = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    max_dist = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    results = find_duplicate_intersections(city_name, min_dist, max_dist)
    results = sorted(results, key=lambda x: x['distance'], reverse=True)
    
    if not results:
        print(f"לא נמצאו מפגשי רחובות כפולים ב-{city_name}")
    else:
        print("\n" + "="*80)
        print(f"מפגשי רחובות כפולים ב{city_name}".center(80))
        print(f"נמצאו {len(results)} תוצאות".center(80))
        if max_dist:
            print(f"מרחק: {min_dist}-{max_dist} מטר".center(80))
        else:
            print(f"מרחק מינימלי: {min_dist} מטר".center(80))
        print("="*80 + "\n")
        
        for i, r in enumerate(results[:20], 1):  # Show top 20
            print(f"#{i:3d} │ {r['street1']} ⚬ {r['street2']}")
            print(f"      │ מרחק: {r['distance']:.0f} מטר")
            print(f"      │ מיקום 1: https://maps.google.com/?q={r['location1'][0]:.6f},{r['location1'][1]:.6f}")
            print(f"      │ מיקום 2: https://maps.google.com/?q={r['location2'][0]:.6f},{r['location2'][1]:.6f}")
            print(f"      └─────────────────────────────────────────────────────────────────────────\n")
        
        if len(results) > 20:
            print(f"... ועוד {len(results) - 20} תוצאות\n")
        
        print("מייצא קבצים...")
        export_to_csv(results, city_name)
        export_to_json(results, city_name)
        export_to_html(results, city_name)
        print(f"\n✓ סיום! פתח את {city_name}_intersections.html בדפדפן לראות מפה אינטראקטיבית")
