# מפגשי רחובות כפולים בישראל

ניתוח של מפגשי רחובות כפולים בערים בישראל באמצעות נתוני OpenStreetMap.

## צפייה במפה

**[מפה אינטראקטיבית של כל התוצאות](https://baobabprince.github.io/israel-duplicate-street-intersections/)**

## מה זה?

מפגש רחובות כפול זה כשאותם שני רחובות נפגשים יותר מפעם אחת במרחק משמעותי (מעל 150 מטר). זה יכול לקרות בגלל תכנון עירוני מעניין, רחובות מקבילים, או פשוט רשת רחובות מורכבת.

## תוצאות

נמצאו 684 מפגשים כאלה ב-63 ערים בישראל.

**הערים עם הכי הרבה תוצאות:**
- ירושלים - 91 מפגשים (המרחק הגדול ביותר: 2,046 מטר)
- באר שבע - 59 מפגשים
- חיפה - 38 מפגשים
- אשקלון - 33 מפגשים
- ראשון לציון - 31 מפגשים

**דוגמאות מעניינות:**
- ירושלים: Military Road ⚬ طريق عسكري - 2,046 מטר
- חיפה: דרך יפו ⚬ שדרות בן גוריון - 1,828 מטר
- רעננה: אחוזה ⚬ הרצל - 1,788 מטר

## איך להריץ

התקנה:
```bash
pip install requests
```

ניתוח עיר אחת:
```bash
python find_duplicate_intersections.py "ירושלים"
```

עם סינון מרחק (מינימום-מקסימום):
```bash
python find_duplicate_intersections.py "תל אביב-יפו" 200 1000
```

ניתוח כל הערים:
```bash
python run_all_cities.py
```

יצירת קובץ מאוחד:
```bash
python create_unified_results.py
```

## מבנה

```
.
├── find_duplicate_intersections.py  # סקריפט ראשי
├── run_all_cities.py                # ריצה על כל הערים
├── create_unified_results.py        # יצירת קובץ מאוחד
├── duplicate_intersections_results/ # תוצאות
│   ├── all_cities_unified.html      # מפה מאוחדת
│   ├── all_cities_unified.csv
│   ├── all_cities_unified.json
│   └── [תיקיות לפי ערים]
└── README.md
```

## איך זה עובד

1. מוריד נתוני רחובות מ-OpenStreetMap
2. מזהה את כל הצמתים שבהם רחובות נפגשים
3. מחפש זוגות רחובות שנפגשים יותר מפעם אחת
4. מסנן שמות דומים (כמו "גולדה מאיר" ו"שדרות גולדה מאיר")
5. שומר רק את המפגש הרחוק ביותר לכל זוג רחובות
6. מייצא למפות HTML, CSV, ו-JSON

## טכנולוגיות

- Python 3
- OpenStreetMap Overpass API
- Leaflet.js
- חישוב מרחקים עם Haversine

## רישיון

MIT

## קרדיטים

נתוני רחובות מ-[OpenStreetMap](https://www.openstreetmap.org/)

---

Created with [Kiro](https://aws.amazon.com/q/developer/)
