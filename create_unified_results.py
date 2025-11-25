#!/usr/bin/env python3
import os
import json
import csv
from pathlib import Path

def create_unified_results():
    results_dir = Path("duplicate_intersections_results")
    all_results = []
    
    # Collect all results from city directories
    for city_dir in results_dir.iterdir():
        if city_dir.is_dir():
            json_file = city_dir / f"{city_dir.name}_intersections.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    city_results = json.load(f)
                    for result in city_results:
                        result['city'] = city_dir.name
                        all_results.append(result)
    
    # Sort by distance (descending)
    all_results.sort(key=lambda x: x['distance'], reverse=True)
    
    # Save unified JSON
    with open(results_dir / "all_cities_unified.json", 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # Save unified CSV
    with open(results_dir / "all_cities_unified.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['עיר', 'רחוב 1', 'רחוב 2', 'מרחק (מטר)', 'קו רוחב 1', 'קו אורך 1', 'קו רוחב 2', 'קו אורך 2'])
        for r in all_results:
            writer.writerow([
                r['city'], r['street1'], r['street2'], f"{r['distance']:.0f}",
                r['location1'][0], r['location1'][1], r['location2'][0], r['location2'][1]
            ])
    
    # Create unified HTML with all cities
    create_unified_html(all_results, results_dir)
    
    print(f"✓ נוצרו קבצים מאוחדים עם {len(all_results)} תוצאות מ-{len(set(r['city'] for r in all_results))} ערים")
    print(f"  - all_cities_unified.json")
    print(f"  - all_cities_unified.csv")
    print(f"  - all_cities_unified.html")

def create_unified_html(results, results_dir):
    if not results:
        return
    
    center_lat = sum(r['location1'][0] + r['location2'][0] for r in results) / (2 * len(results))
    center_lon = sum(r['location1'][1] + r['location2'][1] for r in results) / (2 * len(results))
    
    # Group by city for the list
    cities = {}
    for r in results:
        if r['city'] not in cities:
            cities[r['city']] = []
        cities[r['city']].append(r)
    
    html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="utf-8">
    <title>מפגשי רחובות כפולים - כל הערים בישראל</title>
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
        .city-group {{ border-bottom: 2px solid #ccc; }}
        .city-header {{ padding: 10px 15px; background: #34495e; color: white; font-weight: bold; cursor: pointer; }}
        .city-header:hover {{ background: #2c3e50; }}
        .city-items {{ display: none; }}
        .city-items.open {{ display: block; }}
        .item {{ padding: 12px 15px 12px 30px; border-bottom: 1px solid #ddd; cursor: pointer; transition: background 0.2s; }}
        .item:hover {{ background: #e8e8e8; }}
        .item.active {{ background: #3498db; color: white; }}
        .item-num {{ font-weight: bold; color: #e74c3c; font-size: 12px; }}
        .item.active .item-num {{ color: white; }}
        .item-streets {{ font-size: 13px; margin: 3px 0; }}
        .item-distance {{ font-size: 11px; color: #666; }}
        .item.active .item-distance {{ color: #ecf0f1; }}
    </style>
</head>
<body>
    <div id="info">
        <h1>מפגשי רחובות כפולים בישראל</h1>
        <p class="stats">נמצאו {len(results)} תוצאות ב-{len(cities)} ערים | לחץ על עיר להרחבה ועל תוצאה להתמקדות במפה</p>
    </div>
    <div id="container">
        <div id="list"></div>
        <div id="map"></div>
    </div>
    <script>
        const citiesData = {json.dumps(cities, ensure_ascii=False)};
        
        const map = L.map('map').setView([{center_lat}, {center_lon}], 8);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap'
        }}).addTo(map);
        
        const markers = {{}};
        let globalIndex = 0;
        
        Object.entries(citiesData).forEach(([city, cityResults]) => {{
            cityResults.forEach(item => {{
                globalIndex++;
                const idx = globalIndex;
                const m1 = L.marker([item.location1[0], item.location1[1]]).addTo(map)
                    .bindPopup(`<b>${{city}}</b><br>${{item.street1}} ⚬ ${{item.street2}}<br>מיקום 1<br>מרחק: ${{item.distance.toFixed(0)}}m`);
                const m2 = L.marker([item.location2[0], item.location2[1]]).addTo(map)
                    .bindPopup(`<b>${{city}}</b><br>${{item.street1}} ⚬ ${{item.street2}}<br>מיקום 2<br>מרחק: ${{item.distance.toFixed(0)}}m`);
                const line = L.polyline([[item.location1[0], item.location1[1]], [item.location2[0], item.location2[1]]], 
                    {{color: 'red', weight: 2, opacity: 0.5}}).addTo(map);
                
                markers[idx] = [m1, m2, item];
            }});
        }});
        
        const list = document.getElementById('list');
        let itemIndex = 0;
        
        Object.entries(citiesData).forEach(([city, cityResults]) => {{
            const cityGroup = document.createElement('div');
            cityGroup.className = 'city-group';
            
            const cityHeader = document.createElement('div');
            cityHeader.className = 'city-header';
            cityHeader.textContent = `${{city}} (${{cityResults.length}})`;
            
            const cityItems = document.createElement('div');
            cityItems.className = 'city-items';
            
            cityResults.forEach(item => {{
                itemIndex++;
                const idx = itemIndex;
                const div = document.createElement('div');
                div.className = 'item';
                div.innerHTML = `
                    <div class="item-num">#${{idx}}</div>
                    <div class="item-streets">${{item.street1}} ⚬ ${{item.street2}}</div>
                    <div class="item-distance">מרחק: ${{item.distance.toFixed(0)}} מטר</div>
                `;
                div.onclick = () => {{
                    document.querySelectorAll('.item').forEach(el => el.classList.remove('active'));
                    div.classList.add('active');
                    const midLat = (item.location1[0] + item.location2[0]) / 2;
                    const midLon = (item.location1[1] + item.location2[1]) / 2;
                    map.setView([midLat, midLon], 16);
                    markers[idx][0].openPopup();
                }};
                cityItems.appendChild(div);
            }});
            
            cityHeader.onclick = () => {{
                cityItems.classList.toggle('open');
            }};
            
            cityGroup.appendChild(cityHeader);
            cityGroup.appendChild(cityItems);
            list.appendChild(cityGroup);
        }});
    </script>
</body>
</html>"""
    
    with open(results_dir / "all_cities_unified.html", 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    create_unified_results()
