#!/usr/bin/env python3
"""
Fix the geography database by removing fake countries and getting better data
"""

import sqlite3
import requests

def get_db():
    """Get database connection"""
    db = sqlite3.connect('geography.db')
    db.row_factory = sqlite3.Row
    return db

def remove_fake_antarctica_countries():
    """Remove territories that aren't real countries from Antarctica"""
    db = get_db()
    
    # These are territories/research stations, not countries
    fake_countries = [
        'Bouvet Island',
        'South Georgia and the South Sandwich Islands', 
        'Heard Island and McDonald Islands',
        'French Southern Territories',
        'Antarctica'
    ]
    
    print("🧹 Removing fake Antarctica 'countries'...")
    for country in fake_countries:
        cursor = db.execute('DELETE FROM countries WHERE name = ?', (country,))
        if cursor.rowcount > 0:
            print(f"  ✓ Removed: {country}")
    
    db.commit()
    db.close()

def get_better_country_data():
    """Get comprehensive country data from a better source"""
    print("\n📡 Getting comprehensive country data from REST Countries API...")
    
    try:
        # REST Countries API has all UN recognized countries
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,cca2,cca3,capital,currencies,region,subregion', timeout=15)
        response.raise_for_status()
        countries = response.json()
        
        print(f"  ✓ Found {len(countries)} countries from REST Countries API")
        return countries
        
    except Exception as e:
        print(f"  ✗ Error getting REST Countries data: {e}")
        return []

def map_region_to_continent(region, subregion):
    """Map REST Countries regions to our continent codes"""
    region_mapping = {
        'Africa': 'AF',
        'Asia': 'AS',
        'Europe': 'EU', 
        'Americas': 'NA',  # Default to North America
        'Oceania': 'OC',
        'Antarctic': 'AN'
    }
    
    # More specific mappings for Americas
    if region == 'Americas':
        if subregion in ['South America']:
            return 'SA'
        else:
            return 'NA'  # North/Central America and Caribbean
    
    return region_mapping.get(region, 'AS')  # Default to Asia

def add_missing_countries(countries_data):
    """Add missing countries from the better data source"""
    db = get_db()
    
    # Get continent mapping
    cursor = db.execute('SELECT id, code FROM continents')
    continent_mapping = {row['code']: row['id'] for row in cursor.fetchall()}
    
    # Get existing countries
    cursor = db.execute('SELECT code_iso2 FROM countries')
    existing_countries = {row['code_iso2'] for row in cursor.fetchall()}
    
    print(f"\n🌍 Adding missing countries...")
    added_count = 0
    
    for country in countries_data:
        iso2_code = country.get('cca2', '')
        country_name = country.get('name', {}).get('common', '')
        
        if not iso2_code or not country_name:
            continue
            
        if iso2_code in existing_countries:
            continue
            
        # Skip Antarctica and research stations
        if country.get('region') == 'Antarctic':
            continue
            
        # Get continent
        region = country.get('region', '')
        subregion = country.get('subregion', '')
        continent_code = map_region_to_continent(region, subregion)
        continent_id = continent_mapping.get(continent_code, continent_mapping.get('AS'))
        
        # Get other data
        iso3_code = country.get('cca3', '')
        capital = ''
        if country.get('capital') and len(country['capital']) > 0:
            capital = country['capital'][0]
            
        currency = ''
        if country.get('currencies'):
            # Get first currency code
            currency_codes = list(country['currencies'].keys())
            if currency_codes:
                currency = currency_codes[0]
        
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
                'English'  # Default
            ))
            
            added_count += 1
            print(f"  ✓ Added: {country_name} ({iso2_code})")
            
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️ Skipped {country_name}: {e}")
    
    db.commit()
    db.close()
    
    return added_count

def show_final_stats():
    """Show final database statistics"""
    db = get_db()
    
    print("\n📊 Final Database Statistics:")
    
    cursor = db.execute('''
        SELECT cont.name, COUNT(c.id) as count
        FROM continents cont
        LEFT JOIN countries c ON cont.id = c.continent_id
        GROUP BY cont.id, cont.name
        ORDER BY count DESC
    ''')
    
    total = 0
    for row in cursor.fetchall():
        count = row['count']
        total += count
        print(f"   {row['name']}: {count} countries")
    
    print(f"\n   Total Real Countries: {total}")
    db.close()

def main():
    print("🔧 Geography Database Fixer")
    print("=" * 40)
    
    # Remove fake Antarctica countries
    remove_fake_antarctica_countries()
    
    # Get better country data
    better_data = get_better_country_data()
    
    if better_data:
        # Add missing countries
        added = add_missing_countries(better_data)
        print(f"\n✅ Added {added} missing countries")
    
    # Show final stats
    show_final_stats()
    
    print(f"\n🚀 Database cleanup complete!")
    print("Refresh your browser to see the updated country list.")

if __name__ == '__main__':
    main() 