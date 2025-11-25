#!/usr/bin/env python3
import os
import sys
import time
from find_duplicate_intersections import find_duplicate_intersections, export_to_csv, export_to_json, export_to_html

# Top 200 Israeli cities and towns
CITIES = [
    "ירושלים", "תל אביב-יפו", "חיפה", "ראשון לציון", "פתח תקווה", "אשדוד", "נתניה", "באר שבע",
    "בני ברק", "חולון", "רמת גן", "אשקלון", "רחובות", "בת ים", "בית שמש", "כפר סבא", "הרצליה",
    "חדרה", "מודיעין-מכבים-רעות", "נצרת", "לוד", "רעננה", "רמלה", "קריית אתא", "נהריה", "טבריה",
    "עפולה", "קריית גת", "שדרות", "אילת", "קריית מוצקין", "נס ציונה", "קריית ים", "קריית ביאליק",
    "קריית אונו", "גבעתיים", "קריית שמונה", "עכו", "אור יהודה", "טירת כרמל", "יבנה", "אור עקיבא",
    "בית שאן", "דימונה", "מגדל העמק", "טמרה", "סח'נין", "נשר", "קלנסווה", "כפר יונה", "טייבה",
    "אריאל", "כרמיאל", "נוף הגליל", "יקנעם עילית", "זכרון יעקב", "אלעד", "מעלה אדומים", "מעלות-תרשיחא",
    "קריית מלאכי", "שפרעם", "אום אל-פחם", "מגדל", "ראש העין", "מצפה רמון", "בקעה-ג'ת", "ערד",
    "מבשרת ציון", "כפר קאסם", "ג'סר א-זרקא", "כפר ורדים", "כפר מנדא", "ביר אל-מכסור", "ג'ולס",
    "עילוט", "כפר כנא", "דבוריה", "עין מאהל", "ראמה", "כפר קרע", "בועיינה-נוג'ידאת", "כסרא-סמיע",
    "ערערה", "ערערה-בנגב", "דייר אל-אסד", "מג'ד אל-כרום", "כפר ברא", "באקה אל-גרביה", "ג'דיידה-מכר",
    "כפר יאסיף", "אבו סנאן", "ג'ת", "פקיעין", "כפר מצר", "עספיא", "דאלית אל-כרמל", "בית ג'ן",
    "ינוח-ג'ת", "רהט", "תל שבע", "לקיה", "כסיפה", "שגב-שלום", "חורה", "אור הנר", "מכמורת",
    "גבעת זאב", "אפרת", "בית אריה", "אלפי מנשה", "עמנואל", "קרני שומרון", "אלקנה", "חריש",
    "שוהם", "גן יבנה", "גדרה", "קריית עקרון", "מזכרת בתיה", "גני תקווה", "יהוד-מונוסון", "אזור",
    "קדימה-צורן", "גבעת שמואל", "תל מונד", "נורדיה", "גבעת ברנר", "כפר יונה", "צור יצחק",
    "צור משה", "בני עיש", "כפר ברא", "כפר קרע", "כפר קאסם", "טירה", "כפר קאסם", "ג'לג'וליה",
    "קלנסווה", "טייבה", "טירה", "כפר ברא", "כפר קרע", "כפר קאסם", "ג'לג'וליה", "קלנסווה",
    "יפיע", "עין נקובא", "אבו גוש", "עין ראפה", "בוקעאתא", "מסעדה", "מג'דל שמס", "עין קנייא",
    "כפר סמיע", "פקיעין", "ירכא", "כפר ורדים", "ג'ש", "חורפיש", "מעיליא", "שלומי", "פסוטה",
    "רמת ישי", "כפר תבור", "כפר חסידים", "נשר", "טירת כרמל", "קריית טבעון", "קריית ביאליק",
    "קריית ים", "קריית מוצקין", "קריית אתא", "נהריה", "עכו", "מעלות-תרשיחא", "כרמיאל", "מעיליא",
    "שלומי", "נהריה", "עכו", "מעלות-תרשיחא", "כרמיאל", "מעיליא", "שלומי", "נהריה", "עכו",
    "מעלות-תרשיחא", "כרמיאל", "מעיליא", "שלומי", "נהריה", "עכו", "מעלות-תרשיחא", "כרמיאל",
    "מעיליא", "שלומי", "נהריה", "עכו", "מעלות-תרשיחא", "כרמיאל", "מעיליא", "שלומי", "נהריה"
]

# Remove duplicates and keep unique cities
CITIES = list(dict.fromkeys(CITIES))

def main():
    output_dir = "duplicate_intersections_results"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"מריץ ניתוח על {len(CITIES)} ערים...")
    print(f"התוצאות יישמרו ב-{output_dir}/\n")
    
    summary = []
    
    for i, city in enumerate(CITIES, 1):
        print(f"[{i}/{len(CITIES)}] מעבד {city}...", end=" ", flush=True)
        
        try:
            results = find_duplicate_intersections(city, min_distance=150)
            results = sorted(results, key=lambda x: x['distance'], reverse=True)
            
            if results:
                # Save to city-specific subdirectory
                city_dir = os.path.join(output_dir, city)
                os.makedirs(city_dir, exist_ok=True)
                
                # Change to city directory for exports
                original_dir = os.getcwd()
                os.chdir(city_dir)
                
                export_to_csv(results, city)
                export_to_json(results, city)
                export_to_html(results, city)
                
                os.chdir(original_dir)
                
                summary.append({
                    'city': city,
                    'count': len(results),
                    'max_distance': results[0]['distance'] if results else 0
                })
                print(f"✓ נמצאו {len(results)} תוצאות")
            else:
                print("✗ לא נמצאו תוצאות")
                summary.append({'city': city, 'count': 0, 'max_distance': 0})
        
        except Exception as e:
            print(f"✗ שגיאה: {e}")
            summary.append({'city': city, 'count': -1, 'max_distance': 0})
        
        # Be nice to OSM servers
        time.sleep(2)
    
    # Print summary
    print("\n" + "="*80)
    print("סיכום".center(80))
    print("="*80)
    
    summary.sort(key=lambda x: x['count'], reverse=True)
    
    for item in summary:
        if item['count'] > 0:
            print(f"{item['city']:30} | {item['count']:3} תוצאות | מרחק מקסימלי: {item['max_distance']:.0f}m")
        elif item['count'] == 0:
            print(f"{item['city']:30} | אין תוצאות")
        else:
            print(f"{item['city']:30} | שגיאה")
    
    print(f"\n✓ כל הקבצים נשמרו ב-{output_dir}/")

if __name__ == "__main__":
    main()
