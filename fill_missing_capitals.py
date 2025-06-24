#!/usr/bin/env python3
"""
Fill in missing capital cities for the remaining countries in temporal database.
"""

import sqlite3

# Missing capitals data
MISSING_CAPITALS = {
    "Aland Islands": "Mariehamn",
    "Antarctica": None,  # No permanent capital
    "Argentina": "Buenos Aires",
    "Bonaire, Saint Eustatius and Saba": "Kralendijk",
    "Bouvet Island": None,  # Uninhabited
    "British Indian Ocean Territory": "Diego Garcia",
    "Bulgaria": "Sofia",
    "Colombia": "Bogotá",
    "Curacao": "Willemstad",
    "Democratic Republic of the Congo": "Kinshasa",
    "East Timor": "Dili",
    "French Southern and Antarctic Lands": "Port-aux-Français",
    "Guinea-Bissau": "Bissau",
    "Heard Island and McDonald Islands": None,  # Uninhabited
    "Macao": "Macao",
    "Macedonia": "Skopje",  # North Macedonia
    "Niger": "Niamey",
    "Palestinian Territory": "Ramallah",
    "Pitcairn": "Adamstown",
    "Republic of the Congo": "Brazzaville",
    "Reunion": "Saint-Denis",
    "Saint Barthelemy": "Gustavia",
    "Saint Martin": "Marigot",
    "Sao Tome and Principe": "São Tomé",
    "Seychelles": "Victoria",
    "South Georgia": "King Edward Point",
    "South Korea": "Seoul",
    "Spain": "Madrid",
    "Svalbard and Jan Mayen": "Longyearbyen",
    "Swaziland": "Mbabane",  # Now called Eswatini
    "Turks and Caicos Islands": "Cockburn Town",
    "U.S. Virgin Islands": "Charlotte Amalie",
    "United States Minor Outlying Islands": None,  # Various uninhabited islands
    "Vatican": "Vatican City",
    "Zimbabwe": "Harare"
}

def fill_missing_capitals():
    """Fill in the missing capital cities."""
    
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        updated_count = 0
        
        for country, capital in MISSING_CAPITALS.items():
            if capital:  # Only update if capital exists (not None for uninhabited places)
                cursor.execute('''
                    UPDATE countries_temporal 
                    SET capital = ? 
                    WHERE name = ? AND (capital IS NULL OR capital = '')
                ''', (capital, country))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    print(f"✅ {country}: {capital}")
                else:
                    print(f"⚠️  {country}: Not found in database or already has capital")
            else:
                print(f"🏔️  {country}: No capital (uninhabited/special territory)")
        
        # Verify final count
        cursor.execute('''
            SELECT year, COUNT(*) as countries_with_capitals
            FROM countries_temporal 
            WHERE capital IS NOT NULL AND capital != ''
            GROUP BY year
            ORDER BY year
        ''')
        
        print(f"\n📊 FINAL VERIFICATION - Countries with capitals by year:")
        for row in cursor.fetchall():
            year, count = row
            print(f"   {year}: {count} countries")
        
        # Show countries still missing capitals
        cursor.execute('''
            SELECT DISTINCT name 
            FROM countries_temporal 
            WHERE capital IS NULL OR capital = ''
            ORDER BY name
        ''')
        
        remaining_missing = [row[0] for row in cursor.fetchall()]
        if remaining_missing:
            print(f"\n🔍 Countries still missing capitals ({len(remaining_missing)}):")
            for country in remaining_missing:
                print(f"   - {country}")
        else:
            print(f"\n🎉 All countries now have capitals assigned!")
        
        # Commit changes
        conn.commit()
        print(f"\n💾 Updated {updated_count} countries with missing capitals")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🏛️ FILLING MISSING CAPITAL CITIES")
    print("=" * 50)
    
    success = fill_missing_capitals()
    
    if success:
        print("\n✅ Successfully filled missing capitals!")
    else:
        print("\n❌ Failed to fill missing capitals") 