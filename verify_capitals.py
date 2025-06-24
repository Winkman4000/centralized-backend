#!/usr/bin/env python3
"""
Verify capital cities data in temporal database
"""

import sqlite3

def verify_capitals():
    """Verify capital cities are properly stored."""
    
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        # Get sample of countries with capitals for 2025
        cursor.execute('''
            SELECT name, capital, population, continent_id
            FROM countries_temporal 
            WHERE year = 2025 AND capital IS NOT NULL
            ORDER BY population DESC
            LIMIT 20
        ''')
        
        print("🏛️ TOP 20 COUNTRIES BY POPULATION WITH CAPITALS (2025)")
        print("=" * 70)
        
        for row in cursor.fetchall():
            name, capital, population, continent_id = row
            pop_text = f"{population:,}" if population else "No data"
            print(f"🌍 {name:<25} 🏛️ {capital:<20} 👥 {pop_text}")
        
        # Check capital consistency across years
        print(f"\n🕐 CAPITAL CONSISTENCY CHECK (2020-2025)")
        print("=" * 70)
        
        cursor.execute('''
            SELECT name, capital, COUNT(DISTINCT capital) as capital_variations
            FROM countries_temporal 
            WHERE capital IS NOT NULL
            GROUP BY name
            HAVING capital_variations > 1
            ORDER BY name
        ''')
        
        capital_changes = cursor.fetchall()
        if capital_changes:
            print("⚠️  Countries with capital changes:")
            for row in capital_changes:
                name, capital, variations = row
                print(f"   {name}: {variations} different capitals recorded")
        else:
            print("✅ No capital changes detected across all years (2020-2025)")
        
        # Statistics
        cursor.execute('''
            SELECT 
                year,
                COUNT(*) as total_countries,
                COUNT(capital) as countries_with_capitals,
                ROUND(COUNT(capital) * 100.0 / COUNT(*), 1) as coverage_percent
            FROM countries_temporal
            GROUP BY year
            ORDER BY year
        ''')
        
        print(f"\n📊 CAPITAL DATA COVERAGE BY YEAR")
        print("=" * 70)
        print(f"{'Year':<6} {'Total':<8} {'With Capitals':<15} {'Coverage':<10}")
        print("-" * 45)
        
        for row in cursor.fetchall():
            year, total, with_capitals, coverage = row
            print(f"{year:<6} {total:<8} {with_capitals:<15} {coverage}%")
        
        # Sample of countries without capitals
        cursor.execute('''
            SELECT DISTINCT name
            FROM countries_temporal 
            WHERE capital IS NULL OR capital = ''
            ORDER BY name
            LIMIT 10
        ''')
        
        missing_capitals = [row[0] for row in cursor.fetchall()]
        if missing_capitals:
            print(f"\n🔍 SAMPLE COUNTRIES WITHOUT CAPITALS:")
            print("=" * 70)
            for country in missing_capitals:
                print(f"   ❌ {country}")
        
        print(f"\n✅ Capital verification completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🏛️ VERIFYING CAPITAL CITIES DATA")
    print("=" * 70)
    verify_capitals() 