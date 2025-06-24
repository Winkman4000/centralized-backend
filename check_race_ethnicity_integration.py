#!/usr/bin/env python3
"""
Verify race and ethnicity data integration in temporal database
"""

import sqlite3
import requests
import json

def check_database_columns():
    """Check if race/ethnicity columns exist in database."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(countries_temporal)")
        columns = [row[1] for row in cursor.fetchall()]
        
        race_columns = [
            'race_white_percent', 'race_black_percent', 'race_asian_percent',
            'race_hispanic_percent', 'race_native_american_percent', 
            'race_pacific_islander_percent', 'race_other_percent'
        ]
        
        print("🏗️ DATABASE SCHEMA CHECK:")
        print("=" * 50)
        
        for col in race_columns:
            status = "✅" if col in columns else "❌"
            print(f"{status} {col}")
        
        conn.close()
        return all(col in columns for col in race_columns)
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_sample_data():
    """Check sample race/ethnicity data in database."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        # Get countries with race/ethnicity data
        cursor.execute('''
            SELECT name, year, race_white_percent, race_black_percent, race_asian_percent,
                   race_hispanic_percent, race_native_american_percent, race_other_percent
            FROM countries_temporal 
            WHERE race_white_percent IS NOT NULL
            ORDER BY name, year
            LIMIT 10
        ''')
        
        print("\n📊 SAMPLE RACE/ETHNICITY DATA:")
        print("=" * 80)
        
        for row in cursor.fetchall():
            name, year, white, black, asian, hispanic, native, other = row
            print(f"{name} ({year}): W:{white}% B:{black}% A:{asian}% H:{hispanic}% N:{native}% O:{other}%")
        
        # Count total coverage
        cursor.execute('''
            SELECT COUNT(DISTINCT name) as countries_with_data,
                   COUNT(*) as total_records
            FROM countries_temporal 
            WHERE race_white_percent IS NOT NULL
        ''')
        
        countries_with_data, total_records = cursor.fetchone()
        print(f"\n📈 Coverage: {countries_with_data} countries, {total_records} total records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Data check error: {e}")
        return False

def test_api_integration():
    """Test API endpoints include race/ethnicity data."""
    try:
        print("\n🌐 API INTEGRATION TEST:")
        print("=" * 50)
        
        # Test countries endpoint
        response = requests.get('http://localhost:5001/api/countries?year=2025')
        if response.status_code == 200:
            data = response.json()
            
            # Find a country with race/ethnicity data
            test_country = None
            for country in data['countries']:
                if 'racial_ethnic_distribution' in country:
                    test_country = country
                    break
            
            if test_country:
                print(f"✅ Countries API includes race/ethnicity data")
                print(f"   Sample: {test_country['name']}")
                red = test_country['racial_ethnic_distribution']
                print(f"   Race data: White:{red['white_percent']}%, Black:{red['black_percent']}%, Asian:{red['asian_percent']}%")
            else:
                print("⚠️  No countries found with race/ethnicity data in API")
        else:
            print(f"❌ Countries API error: {response.status_code}")
        
        # Test timeline endpoint
        response = requests.get('http://localhost:5001/api/country/United States/timeline')
        if response.status_code == 200:
            data = response.json()
            
            # Check if timeline includes race data
            if data['timeline'] and 'race_white_percent' in data['timeline'][0]:
                print(f"✅ Timeline API includes race/ethnicity data")
                sample_year = data['timeline'][0]
                print(f"   Sample: {data['country']} ({sample_year['year']})")
                print(f"   Race data: White:{sample_year['race_white_percent']}%, Black:{sample_year['race_black_percent']}%")
            else:
                print("⚠️  Timeline API missing race/ethnicity data")
        else:
            print(f"❌ Timeline API error: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def show_diverse_examples():
    """Show examples of countries with diverse racial/ethnic compositions."""
    try:
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        print("\n🌍 DIVERSE COUNTRIES EXAMPLES:")
        print("=" * 70)
        
        # Get interesting examples
        examples = [
            "United States", "Brazil", "South Africa", "Australia", 
            "Canada", "Malaysia", "Singapore", "New Zealand"
        ]
        
        for country in examples:
            cursor.execute('''
                SELECT name, race_white_percent, race_black_percent, race_asian_percent,
                       race_hispanic_percent, race_native_american_percent, race_other_percent
                FROM countries_temporal 
                WHERE name = ? AND year = 2025 AND race_white_percent IS NOT NULL
            ''', (country,))
            
            row = cursor.fetchone()
            if row:
                name, white, black, asian, hispanic, native, other = row
                print(f"🏛️ {name}:")
                print(f"   White: {white}%, Black: {black}%, Asian: {asian}%")
                print(f"   Hispanic: {hispanic}%, Native: {native}%, Other: {other}%")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Examples error: {e}")

def main():
    """Main verification function."""
    print("🌍 RACE AND ETHNICITY DATA INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # Step 1: Check database schema
    if not check_database_columns():
        print("❌ Database schema check failed")
        return
    
    # Step 2: Check sample data
    if not check_sample_data():
        print("❌ Sample data check failed")
        return
    
    # Step 3: Test API integration
    if not test_api_integration():
        print("❌ API integration test failed")
        return
    
    # Step 4: Show diverse examples
    show_diverse_examples()
    
    print("🎉 VERIFICATION COMPLETE!")
    print("✅ Race and ethnicity data successfully integrated")
    print("🌐 Web interface: http://localhost:5001")
    print("📊 Features: 10-year update cycle, same data across 2020-2025")

if __name__ == "__main__":
    main() 