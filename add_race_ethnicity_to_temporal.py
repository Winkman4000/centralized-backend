#!/usr/bin/env python3
"""
Add race and ethnic distribution data to the temporal geography database.
Following 10-year update cycle like religious data - same distributions for all years 2020-2025.
Based on latest census data and demographic surveys from various authoritative sources.
"""

import sqlite3
import sys

# Race and ethnic distribution data for major countries
# Based on latest census data (2020-2022) and demographic surveys
# Percentages represent major racial/ethnic groups, may not sum to 100% due to mixed/other categories
RACE_ETHNICITY_DATA = {
    # Major countries with comprehensive race/ethnicity data
    "United States": {
        "race_white_percent": 61.6,
        "race_black_percent": 13.4,
        "race_asian_percent": 6.0,
        "race_hispanic_percent": 18.5,
        "race_native_american_percent": 1.3,
        "race_pacific_islander_percent": 0.2,
        "race_other_percent": 4.0
    },
    
    "Canada": {
        "race_white_percent": 69.8,
        "race_black_percent": 3.5,
        "race_asian_percent": 17.7,
        "race_hispanic_percent": 1.3,
        "race_native_american_percent": 5.0,
        "race_pacific_islander_percent": 0.1,
        "race_other_percent": 2.6
    },
    
    "Brazil": {
        "race_white_percent": 43.1,
        "race_black_percent": 10.2,
        "race_asian_percent": 1.1,
        "race_hispanic_percent": 0.0,  # Mixed into other categories
        "race_native_american_percent": 0.5,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 45.1  # Mixed race (Pardo)
    },
    
    "United Kingdom": {
        "race_white_percent": 81.7,
        "race_black_percent": 3.3,
        "race_asian_percent": 9.3,
        "race_hispanic_percent": 1.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 4.7
    },
    
    "Australia": {
        "race_white_percent": 72.6,
        "race_black_percent": 0.4,
        "race_asian_percent": 17.4,
        "race_hispanic_percent": 1.2,
        "race_native_american_percent": 3.3,  # Aboriginal and Torres Strait Islander
        "race_pacific_islander_percent": 1.2,
        "race_other_percent": 3.9
    },
    
    "South Africa": {
        "race_white_percent": 7.8,
        "race_black_percent": 81.0,
        "race_asian_percent": 2.5,
        "race_hispanic_percent": 0.1,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 8.6  # Coloured population
    },
    
    "New Zealand": {
        "race_white_percent": 64.1,
        "race_black_percent": 0.4,
        "race_asian_percent": 15.3,
        "race_hispanic_percent": 1.5,
        "race_native_american_percent": 16.5,  # Māori
        "race_pacific_islander_percent": 8.1,
        "race_other_percent": 2.2
    },
    
    "Germany": {
        "race_white_percent": 81.5,
        "race_black_percent": 1.0,
        "race_asian_percent": 4.0,
        "race_hispanic_percent": 0.5,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 13.0  # Various immigrant backgrounds
    },
    
    "France": {
        "race_white_percent": 85.0,  # Estimated (France doesn't collect official race data)
        "race_black_percent": 3.0,
        "race_asian_percent": 4.0,
        "race_hispanic_percent": 1.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.1,
        "race_other_percent": 6.9
    },
    
    "Netherlands": {
        "race_white_percent": 76.9,
        "race_black_percent": 2.4,
        "race_asian_percent": 4.8,
        "race_hispanic_percent": 1.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 14.9
    },
    
    # Asian countries with ethnic diversity
    "China": {
        "race_white_percent": 0.1,
        "race_black_percent": 0.0,
        "race_asian_percent": 91.6,  # Han Chinese
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 8.3  # 55 ethnic minorities
    },
    
    "India": {
        "race_white_percent": 0.1,
        "race_black_percent": 0.2,
        "race_asian_percent": 72.0,  # Indo-Aryan
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 8.6,  # Scheduled tribes
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 19.1  # Dravidian and others
    },
    
    "Japan": {
        "race_white_percent": 0.2,
        "race_black_percent": 0.1,
        "race_asian_percent": 98.1,
        "race_hispanic_percent": 0.1,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 1.5
    },
    
    "Singapore": {
        "race_white_percent": 2.0,
        "race_black_percent": 0.2,
        "race_asian_percent": 74.3,  # Chinese majority
        "race_hispanic_percent": 0.1,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 23.4  # Malay, Indian, others
    },
    
    "Malaysia": {
        "race_white_percent": 0.3,
        "race_black_percent": 0.1,
        "race_asian_percent": 69.1,  # Malay and Chinese
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 12.8,  # Indigenous groups
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 17.7  # Indian and others
    },
    
    # Middle Eastern countries
    "Israel": {
        "race_white_percent": 44.9,  # Ashkenazi Jewish
        "race_black_percent": 2.0,
        "race_asian_percent": 4.2,
        "race_hispanic_percent": 0.2,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 48.7  # Sephardic, Mizrahi, Arab
    },
    
    "Turkey": {
        "race_white_percent": 7.0,
        "race_black_percent": 0.5,
        "race_asian_percent": 3.0,
        "race_hispanic_percent": 0.1,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 89.4  # Turkish, Kurdish, others
    },
    
    # African countries with ethnic diversity
    "Nigeria": {
        "race_white_percent": 0.1,
        "race_black_percent": 95.0,
        "race_asian_percent": 0.2,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 4.7  # Various ethnic groups
    },
    
    "Kenya": {
        "race_white_percent": 0.3,
        "race_black_percent": 97.6,
        "race_asian_percent": 0.8,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 1.3
    },
    
    "Ethiopia": {
        "race_white_percent": 0.1,
        "race_black_percent": 98.5,
        "race_asian_percent": 0.2,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 0.0,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 1.2
    },
    
    # Latin American countries
    "Mexico": {
        "race_white_percent": 47.0,
        "race_black_percent": 1.2,
        "race_asian_percent": 1.0,
        "race_hispanic_percent": 0.0,  # Integrated into other categories
        "race_native_american_percent": 10.5,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 40.3  # Mestizo (mixed)
    },
    
    "Argentina": {
        "race_white_percent": 85.0,
        "race_black_percent": 0.4,
        "race_asian_percent": 3.4,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 2.4,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 8.8
    },
    
    "Colombia": {
        "race_white_percent": 37.5,
        "race_black_percent": 9.3,
        "race_asian_percent": 0.3,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 4.4,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 48.5  # Mestizo and mixed
    },
    
    "Peru": {
        "race_white_percent": 5.9,
        "race_black_percent": 3.6,
        "race_asian_percent": 3.0,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 25.8,
        "race_pacific_islander_percent": 0.0,
        "race_other_percent": 61.7  # Mestizo
    },
    
    "Chile": {
        "race_white_percent": 64.1,
        "race_black_percent": 0.1,
        "race_asian_percent": 1.2,
        "race_hispanic_percent": 0.0,
        "race_native_american_percent": 12.8,
        "race_pacific_islander_percent": 0.1,
        "race_other_percent": 21.7
    }
}

def add_race_ethnicity_columns():
    """Add race and ethnicity columns to countries_temporal table."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(countries_temporal)")
        columns = [row[1] for row in cursor.fetchall()]
        
        race_ethnicity_columns = [
            'race_white_percent',
            'race_black_percent', 
            'race_asian_percent',
            'race_hispanic_percent',
            'race_native_american_percent',
            'race_pacific_islander_percent',
            'race_other_percent'
        ]
        
        # Add missing columns
        for column in race_ethnicity_columns:
            if column not in columns:
                cursor.execute(f'ALTER TABLE countries_temporal ADD COLUMN {column} REAL')
                print(f"✅ Added column: {column}")
        
        conn.commit()
        conn.close()
        print("🏗️ Database schema updated successfully")
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False
    
    return True

def update_race_ethnicity_data():
    """Update race and ethnicity data for all countries and years."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        updated_countries = 0
        total_records = 0
        
        print("🎨 Updating race and ethnicity data...")
        
        for country_name, race_data in RACE_ETHNICITY_DATA.items():
            # Update all years for this country
            cursor.execute('''
                UPDATE countries_temporal 
                SET race_white_percent = ?,
                    race_black_percent = ?,
                    race_asian_percent = ?,
                    race_hispanic_percent = ?,
                    race_native_american_percent = ?,
                    race_pacific_islander_percent = ?,
                    race_other_percent = ?
                WHERE name = ?
            ''', (
                race_data['race_white_percent'],
                race_data['race_black_percent'],
                race_data['race_asian_percent'],
                race_data['race_hispanic_percent'],
                race_data['race_native_american_percent'],
                race_data['race_pacific_islander_percent'],
                race_data['race_other_percent'],
                country_name
            ))
            
            records_updated = cursor.rowcount
            if records_updated > 0:
                updated_countries += 1
                total_records += records_updated
                print(f"✅ {country_name}: {records_updated} records updated")
            else:
                print(f"⚠️  {country_name}: Country not found in database")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 RACE/ETHNICITY UPDATE SUMMARY:")
        print(f"Countries with data: {updated_countries}")
        print(f"Total records updated: {total_records}")
        print(f"Years covered: 2020-2025 (same data for all years)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating race/ethnicity data: {e}")
        return False

def verify_race_ethnicity_data():
    """Verify the race and ethnicity data was added correctly."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        # Get sample of countries with race/ethnicity data
        cursor.execute('''
            SELECT name, year, race_white_percent, race_black_percent, race_asian_percent, 
                   race_hispanic_percent, race_native_american_percent, race_other_percent
            FROM countries_temporal 
            WHERE race_white_percent IS NOT NULL
            ORDER BY name, year
            LIMIT 15
        ''')
        
        print("\n🔍 VERIFICATION - Sample Race/Ethnicity Data:")
        print("=" * 100)
        
        for row in cursor.fetchall():
            name, year, white, black, asian, hispanic, native, other = row
            print(f"{name} ({year}): White: {white}%, Black: {black}%, Asian: {asian}%, Hispanic: {hispanic}%, Native: {native}%, Other: {other}%")
        
        # Count total countries with race/ethnicity data
        cursor.execute('''
            SELECT COUNT(DISTINCT name) 
            FROM countries_temporal 
            WHERE race_white_percent IS NOT NULL
        ''')
        
        count = cursor.fetchone()[0]
        print(f"\n📈 Total countries with race/ethnicity data: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

def main():
    """Main function to add race and ethnicity data."""
    print("🌍 ADDING RACE AND ETHNICITY DISTRIBUTION DATA")
    print("=" * 60)
    print("Following 10-year update cycle like religious data")
    print("Same distributions will apply to all years 2020-2025")
    print("=" * 60)
    
    # Step 1: Add columns to database
    if not add_race_ethnicity_columns():
        print("❌ Failed to update database schema")
        sys.exit(1)
    
    # Step 2: Update race and ethnicity data
    if not update_race_ethnicity_data():
        print("❌ Failed to update race/ethnicity data")
        sys.exit(1)
    
    # Step 3: Verify the data
    verify_race_ethnicity_data()
    
    print("\n🎉 Race and ethnicity data successfully added!")
    print("💡 Note: This data follows a 10-year update cycle")
    print("🔄 Same percentages apply to all years (2020-2025)")
    print("📅 Can be extended back to 2015 if needed later")

if __name__ == "__main__":
    main() 