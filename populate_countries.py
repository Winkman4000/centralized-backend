#!/usr/bin/env python3
"""
Populate all world countries into the geography database
Uses country.io API for comprehensive country data
"""

import requests
import sqlite3
import json

def get_db():
    """Get database connection"""
    db = sqlite3.connect('geography.db')
    db.row_factory = sqlite3.Row
    return db

def get_continent_mapping():
    """Get mapping of continent codes to our database IDs"""
    db = get_db()
    cursor = db.execute('SELECT id, code FROM continents')
    continents = {row['code']: row['id'] for row in cursor.fetchall()}
    db.close()
    return continents

def download_country_data():
    """Download country data from country.io API"""
    print("📡 Downloading country data from country.io...")
    
    # Download all the data files
    urls = {
        'names': 'https://country.io/names.json',
        'continents': 'https://country.io/continent.json', 
        'iso3': 'https://country.io/iso3.json',
        'capitals': 'https://country.io/capital.json',
        'currencies': 'https://country.io/currency.json',
        'phones': 'https://country.io/phone.json'
    }
    
    data = {}
    for key, url in urls.items():
        try:
            print(f"  Downloading {key}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data[key] = response.json()
            print(f"  ✓ {key}: {len(data[key])} countries")
        except Exception as e:
            print(f"  ✗ Error downloading {key}: {e}")
            data[key] = {}
    
    return data

def map_continent_code(continent_code, continent_mapping):
    """Map continent code to our database ID"""
    # Map country.io continent codes to our database codes
    mapping = {
        'AF': 'AF',  # Africa
        'AS': 'AS',  # Asia  
        'EU': 'EU',  # Europe
        'NA': 'NA',  # North America
        'OC': 'OC',  # Oceania/Australia
        'SA': 'SA',  # South America
        'AN': 'AN'   # Antarctica
    }
    
    mapped_code = mapping.get(continent_code)
    if mapped_code and mapped_code in continent_mapping:
        return continent_mapping[mapped_code]
    
    # Default fallbacks
    if continent_code in ['AF', 'Africa']:
        return continent_mapping.get('AF')
    elif continent_code in ['AS', 'Asia']:
        return continent_mapping.get('AS')
    elif continent_code in ['EU', 'Europe']:
        return continent_mapping.get('EU')
    elif continent_code in ['NA', 'North America']:
        return continent_mapping.get('NA')
    elif continent_code in ['OC', 'Oceania']:
        return continent_mapping.get('OC')
    elif continent_code in ['SA', 'South America']:
        return continent_mapping.get('SA')
    
    # Default to Asia if unknown
    return continent_mapping.get('AS', 1)

def populate_countries(country_data, continent_mapping):
    """Populate countries into the database"""
    db = get_db()
    
    print(f"\n🌍 Populating {len(country_data['names'])} countries...")
    
    # Get existing countries to avoid duplicates
    cursor = db.execute('SELECT code_iso2 FROM countries')
    existing_countries = {row['code_iso2'] for row in cursor.fetchall()}
    
    added_count = 0
    skipped_count = 0
    
    for iso2_code, country_name in country_data['names'].items():
        if iso2_code in existing_countries:
            skipped_count += 1
            continue
            
        # Get continent ID
        continent_code = country_data['continents'].get(iso2_code, 'AS')
        continent_id = map_continent_code(continent_code, continent_mapping)
        
        # Get other data
        iso3_code = country_data['iso3'].get(iso2_code, '')
        capital = country_data['capitals'].get(iso2_code, '')
        currency = country_data['currencies'].get(iso2_code, '')
        
        # Clean up phone code
        phone_code = country_data['phones'].get(iso2_code, '')
        if phone_code.startswith('+'):
            phone_code = phone_code[1:]
        
        try:
            cursor = db.execute('''
                INSERT INTO countries (continent_id, name, code_iso2, code_iso3, capital, currency, language_primary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                continent_id,
                country_name,
                iso2_code,
                iso3_code,
                capital,
                currency,
                'English'  # Default language
            ))
            
            added_count += 1
            
            if added_count % 50 == 0:
                print(f"  Added {added_count} countries...")
                
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️ Skipped {country_name} ({iso2_code}): {e}")
            skipped_count += 1
    
    db.commit()
    db.close()
    
    print(f"\n✅ Country population complete!")
    print(f"   Added: {added_count} countries")
    print(f"   Skipped: {skipped_count} countries")
    
    return added_count

def show_statistics():
    """Show database statistics after population"""
    db = get_db()
    
    print("\n📊 Database Statistics:")
    
    # Count by continent
    cursor = db.execute('''
        SELECT cont.name, cont.code, COUNT(c.id) as country_count
        FROM continents cont
        LEFT JOIN countries c ON cont.id = c.continent_id
        GROUP BY cont.id, cont.name, cont.code
        ORDER BY country_count DESC
    ''')
    
    for row in cursor.fetchall():
        print(f"   {row['name']} ({row['code']}): {row['country_count']} countries")
    
    # Total count
    cursor = db.execute('SELECT COUNT(*) as total FROM countries')
    total = cursor.fetchone()['total']
    print(f"\n   Total Countries: {total}")
    
    db.close()

def main():
    print("🌍 World Countries Database Populator")
    print("=" * 50)
    
    # Check if database exists
    try:
        continent_mapping = get_continent_mapping()
        print(f"✓ Found {len(continent_mapping)} continents in database")
    except Exception as e:
        print(f"✗ Error accessing database: {e}")
        print("Make sure to run 'python app.py' first to create the database!")
        return
    
    # Download country data
    country_data = download_country_data()
    
    if not country_data['names']:
        print("✗ No country data downloaded. Check your internet connection.")
        return
    
    # Populate countries
    added_count = populate_countries(country_data, continent_mapping)
    
    if added_count > 0:
        show_statistics()
        
        print(f"\n🚀 Success! Added {added_count} countries to the database.")
        print("You can now browse them at: http://localhost:5000")
    else:
        print("\n⚠️ No new countries were added.")

if __name__ == '__main__':
    main() 