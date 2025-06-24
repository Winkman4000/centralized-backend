#!/usr/bin/env python3

import sqlite3

def check_missing_countries():
    conn = sqlite3.connect('geography_temporal.db')
    cursor = conn.cursor()
    
    # Get countries with race/ethnicity data
    cursor.execute('SELECT DISTINCT name FROM countries_temporal WHERE race_white_percent IS NOT NULL ORDER BY name')
    countries_with_data = [row[0] for row in cursor.fetchall()]
    
    # Get countries without race/ethnicity data
    cursor.execute('SELECT DISTINCT name FROM countries_temporal WHERE race_white_percent IS NULL ORDER BY name')
    countries_without_data = [row[0] for row in cursor.fetchall()]
    
    # Get total count
    cursor.execute('SELECT COUNT(DISTINCT name) FROM countries_temporal')
    total_countries = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"📊 RACE/ETHNICITY DATA COVERAGE:")
    print(f"✅ Countries WITH data: {len(countries_with_data)}")
    print(f"❌ Countries WITHOUT data: {len(countries_without_data)}")
    print(f"🌍 Total countries: {total_countries}")
    print()
    
    print("🎯 Countries WITH race/ethnicity data:")
    for country in countries_with_data:
        print(f"  ✅ {country}")
    
    print(f"\n❌ Countries WITHOUT race/ethnicity data (first 50):")
    for country in countries_without_data[:50]:
        print(f"  ❌ {country}")
    
    if len(countries_without_data) > 50:
        print(f"  ... and {len(countries_without_data) - 50} more countries")

if __name__ == "__main__":
    check_missing_countries() 