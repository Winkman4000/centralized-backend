#!/usr/bin/env python3

import sqlite3

def add_more_race_ethnicity_data():
    """Add race/ethnicity data for more countries"""
    
    # Additional race/ethnicity data for more countries
    countries_data = {
        # Caribbean and Central America
        'Cuba': {
            'white': 64.1, 'black': 9.3, 'asian': 0.1, 'hispanic': 26.6, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 0.0
        },
        'Jamaica': {
            'white': 0.2, 'black': 92.1, 'asian': 0.8, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 6.9
        },
        'Dominican Republic': {
            'white': 16.0, 'black': 11.0, 'asian': 0.1, 'hispanic': 73.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 0.0
        },
        'Costa Rica': {
            'white': 83.6, 'black': 6.7, 'asian': 2.4, 'hispanic': 0.0, 
            'native_american': 2.4, 'pacific_islander': 0.0, 'other': 4.9
        },
        'Guatemala': {
            'white': 18.5, 'black': 0.2, 'asian': 0.1, 'hispanic': 41.7, 
            'native_american': 39.3, 'pacific_islander': 0.0, 'other': 0.2
        },
        'Panama': {
            'white': 6.8, 'black': 9.2, 'asian': 3.4, 'hispanic': 65.0, 
            'native_american': 12.3, 'pacific_islander': 0.0, 'other': 3.3
        },
        
        # African Countries
        'Angola': {
            'white': 1.0, 'black': 37.0, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 61.9
        },
        'Cameroon': {
            'white': 0.1, 'black': 31.0, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 68.8
        },
        'Democratic Republic of the Congo': {
            'white': 0.1, 'black': 80.0, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 19.8
        },
        'Ivory Coast': {
            'white': 0.1, 'black': 42.1, 'asian': 0.7, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 57.1
        },
        'Mali': {
            'white': 0.1, 'black': 50.0, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 49.8
        },
        'Senegal': {
            'white': 0.1, 'black': 43.3, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 56.5
        },
        'Botswana': {
            'white': 3.0, 'black': 79.0, 'asian': 0.4, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 17.6
        },
        'Namibia': {
            'white': 6.5, 'black': 87.5, 'asian': 0.5, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 5.5
        },
        
        # Asian Countries
        'Afghanistan': {
            'white': 0.1, 'black': 0.3, 'asian': 42.0, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 57.6
        },
        'Sri Lanka': {
            'white': 0.1, 'black': 0.2, 'asian': 74.9, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 24.8
        },
        'Nepal': {
            'white': 0.1, 'black': 0.1, 'asian': 81.3, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 18.5
        },
        'Cambodia': {
            'white': 0.1, 'black': 0.1, 'asian': 97.6, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 2.2
        },
        'Laos': {
            'white': 0.1, 'black': 0.1, 'asian': 67.0, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 32.8
        },
        'Mongolia': {
            'white': 0.2, 'black': 0.1, 'asian': 94.9, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 4.8
        },
        
        # European Countries
        'Serbia': {
            'white': 83.3, 'black': 0.1, 'asian': 0.1, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 16.4
        },
        'Bosnia and Herzegovina': {
            'white': 50.1, 'black': 0.1, 'asian': 0.1, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 49.6
        },
        'Albania': {
            'white': 82.6, 'black': 0.1, 'asian': 0.1, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 17.1
        },
        'Lithuania': {
            'white': 86.4, 'black': 0.1, 'asian': 0.1, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 13.3
        },
        'Latvia': {
            'white': 62.2, 'black': 0.1, 'asian': 0.2, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 37.4
        },
        'Estonia': {
            'white': 68.7, 'black': 0.1, 'asian': 0.2, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 30.9
        },
        'Slovenia': {
            'white': 83.1, 'black': 0.2, 'asian': 0.2, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 16.4
        },
        'Slovakia': {
            'white': 85.8, 'black': 0.1, 'asian': 0.2, 'hispanic': 0.1, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 13.8
        },
        
        # Middle Eastern Countries
        'Lebanon': {
            'white': 95.0, 'black': 0.1, 'asian': 0.5, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 4.4
        },
        'Syria': {
            'white': 90.3, 'black': 0.5, 'asian': 0.2, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 9.0
        },
        'Kuwait': {
            'white': 31.3, 'black': 1.0, 'asian': 37.8, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 29.9
        },
        'Qatar': {
            'white': 13.8, 'black': 1.5, 'asian': 67.7, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 17.0
        },
        'Bahrain': {
            'white': 46.0, 'black': 1.0, 'asian': 45.5, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 7.5
        },
        'Oman': {
            'white': 44.0, 'black': 5.5, 'asian': 43.7, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 6.8
        },
        
        # Oceania
        'Fiji': {
            'white': 1.2, 'black': 0.7, 'asian': 37.6, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 57.3, 'other': 3.2
        },
        'Papua New Guinea': {
            'white': 0.1, 'black': 0.2, 'asian': 0.3, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 96.7, 'other': 2.7
        },
        
        # North American Countries
        'Haiti': {
            'white': 0.2, 'black': 95.0, 'asian': 0.1, 'hispanic': 0.0, 
            'native_american': 0.0, 'pacific_islander': 0.0, 'other': 4.7
        },
        'El Salvador': {
            'white': 12.7, 'black': 0.1, 'asian': 0.7, 'hispanic': 86.3, 
            'native_american': 0.2, 'pacific_islander': 0.0, 'other': 0.0
        },
        'Honduras': {
            'white': 1.0, 'black': 2.1, 'asian': 0.3, 'hispanic': 90.0, 
            'native_american': 7.0, 'pacific_islander': 0.0, 'other': 0.0
        },
        'Nicaragua': {
            'white': 17.0, 'black': 9.0, 'asian': 0.1, 'hispanic': 69.0, 
            'native_american': 5.0, 'pacific_islander': 0.0, 'other': 0.0
        }
    }
    
    conn = sqlite3.connect('geography_temporal.db')
    cursor = conn.cursor()
    
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    countries_updated = 0
    records_updated = 0
    
    print("🌍 Adding race/ethnicity data for more countries...")
    print("=" * 60)
    
    for country_name, data in countries_data.items():
        # Check if country exists in database
        cursor.execute('SELECT COUNT(*) FROM countries_temporal WHERE name = ?', (country_name,))
        if cursor.fetchone()[0] == 0:
            print(f"⚠️  Country '{country_name}' not found in database - skipping")
            continue
            
        # Check if country already has race/ethnicity data
        cursor.execute('SELECT COUNT(*) FROM countries_temporal WHERE name = ? AND race_white_percent IS NOT NULL', (country_name,))
        if cursor.fetchone()[0] > 0:
            print(f"ℹ️  Country '{country_name}' already has race/ethnicity data - skipping")
            continue
        
        # Update all years for this country
        for year in years:
            cursor.execute('''
                UPDATE countries_temporal 
                SET race_white_percent = ?, race_black_percent = ?, race_asian_percent = ?,
                    race_hispanic_percent = ?, race_native_american_percent = ?, 
                    race_pacific_islander_percent = ?, race_other_percent = ?
                WHERE name = ? AND year = ?
            ''', (
                data['white'], data['black'], data['asian'], data['hispanic'],
                data['native_american'], data['pacific_islander'], data['other'],
                country_name, year
            ))
            records_updated += cursor.rowcount
        
        countries_updated += 1
        print(f"✅ {country_name}: White {data['white']}%, Black {data['black']}%, Asian {data['asian']}%, Hispanic {data['hispanic']}%")
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"🎉 RACE/ETHNICITY DATA UPDATE COMPLETE!")
    print(f"📊 Countries updated: {countries_updated}")
    print(f"📈 Total records updated: {records_updated}")
    print(f"🕐 Data applied to years: {', '.join(map(str, years))}")

if __name__ == "__main__":
    add_more_race_ethnicity_data() 