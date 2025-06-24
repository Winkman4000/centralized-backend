#!/usr/bin/env python3
"""
Fill missing 2024 population data in the temporal geography database.
Based on web search results from CIA World Factbook, Worldometers, and other official sources.
"""

import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2024 population data for missing countries from various authoritative sources
MISSING_2024_POPULATIONS = {
    # From CIA World Factbook and Worldometers 2024 data
    'Faroe Islands': 56002,  # From Faroe Islands Statistics 2024
    'Greenland': 55745,      # From CIA World Factbook 2024
    'American Samoa': 46029,  # From CIA World Factbook 2024 
    'Northern Mariana Islands': 43541,  # From CIA World Factbook 2024
    'Turks and Caicos Islands': 46855,  # From CIA World Factbook 2024
    'Cayman Islands': 75844,  # From CIA World Factbook 2024
    'Aruba': 108147,         # From CIA World Factbook 2024
    'Curacao': 185487,       # From Worldometers 2024
    'Sint Maarten': 43923,   # From Worldometers 2024
    'French Polynesia': 282465,  # From Worldometers 2024
    'New Caledonia': 295333,  # From Worldometers 2024
    'Guam': 168999,          # From Worldometers 2024
    'Puerto Rico': 3235289,  # From US Census Bureau 2024
    'U.S. Virgin Islands': 84138,  # From Worldometers 2024
    'British Virgin Islands': 39732,  # From CIA World Factbook 2024
    'Anguilla': 14728,       # From CIA World Factbook 2024
    'Montserrat': 4359,      # From Worldometers 2024
    'Saint Helena, Ascension, and Tristan da Cunha': 5197,  # From CIA World Factbook 2024
    'Falkland Islands': 3469,  # From Worldometers 2024
    'Gibraltar': 40126,      # From Worldometers 2024
    'Bermuda': 64555,        # From Worldometers 2024
    'Saint Pierre and Miquelon': 5574,  # From Worldometers 2024
    'Wallis and Futuna': 11194,  # From Worldometers 2024
    'French Southern Territories': 0,  # Uninhabited research stations
    'Bouvet Island': 0,      # Uninhabited
    'Heard Island and McDonald Islands': 0,  # Uninhabited
    'British Indian Ocean Territory': 0,  # Military base only
    'South Georgia and the South Sandwich Islands': 0,  # Research stations only
    
    # European territories and dependencies
    'Aland Islands': 30500,  # Estimated 2024
    'Svalbard and Jan Mayen': 2600,  # From Norwegian statistics 2024
    'Isle of Man': 84118,    # From Worldometers 2024
    'Jersey': 107800,        # Estimated 2024
    'Guernsey': 67334,       # Estimated 2024
    
    # Pacific territories
    'Norfolk Island': 1750,   # Estimated 2024
    'Christmas Island': 1843, # Estimated 2024
    'Cocos (Keeling) Islands': 596,  # Estimated 2024
    'Cook Islands': 13263,   # From Worldometers 2024
    'Niue': 1821,           # From Worldometers 2024
    'Tokelau': 2608,        # From Worldometers 2024
    'Pitcairn Islands': 50,  # Estimated 2024
    
    # Caribbean and other small territories
    'Saint Barthelemy': 11414,  # From Worldometers 2024
    'Saint Martin': 32489,   # Estimated 2024
    'Caribbean Netherlands': 31338,  # From Worldometers 2024
    
    # African territories
    'Mayotte': 337011,       # From Worldometers 2024
    'Reunion': 882405,       # From Worldometers 2024
    'Western Sahara': 600904, # From Worldometers 2024
    
    # Special cases - Very small populations
    'Vatican City': 501,     # From Worldometers 2024
    'San Marino': 33572,    # From Worldometers 2024
    'Liechtenstein': 40128, # From Worldometers 2024
    'Monaco': 38341,        # From Worldometers 2024
    'Nauru': 12025,         # From Worldometers 2024
    'Tuvalu': 9492,         # From Worldometers 2024
    'Palau': 17663,         # From Worldometers 2024
}

def update_missing_2024_populations():
    """Update missing 2024 population data in the temporal database."""
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        print("🔄 UPDATING MISSING 2024 POPULATION DATA")
        print("=" * 50)
        
        updated_count = 0
        not_found_count = 0
        
        for country_name, population in MISSING_2024_POPULATIONS.items():
            # Try to find the country in the database
            cursor.execute("""
                SELECT id, name FROM countries_temporal 
                WHERE year = 2024 AND (name = ? OR name LIKE ? OR name LIKE ?)
            """, (country_name, f"%{country_name}%", f"{country_name}%"))
            
            result = cursor.fetchone()
            
            if result:
                country_id, db_name = result
                
                # Update the population
                cursor.execute("""
                    UPDATE countries_temporal 
                    SET population = ? 
                    WHERE id = ?
                """, (population, country_id))
                
                print(f"✅ Updated {db_name}: {population:,}")
                updated_count += 1
            else:
                print(f"❌ Not found in database: {country_name}")
                not_found_count += 1
        
        # Commit changes
        conn.commit()
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Updated: {updated_count} countries")
        print(f"❌ Not found: {not_found_count} countries")
        
        # Verify the updates
        print(f"\n🔍 VERIFICATION:")
        cursor.execute("""
            SELECT COUNT(*) as total_countries,
                   COUNT(CASE WHEN population IS NOT NULL AND population > 0 THEN 1 END) as with_population,
                   SUM(CASE WHEN population IS NOT NULL THEN population ELSE 0 END) as total_population
            FROM countries_temporal 
            WHERE year = 2024
        """)
        
        result = cursor.fetchone()
        total, with_pop, total_pop = result
        
        print(f"📈 2024 Status: {with_pop}/{total} countries ({with_pop/total*100:.1f}%) with population data")
        print(f"🌍 Total 2024 population: {total_pop:,}")
        
        # Show some examples of updated countries
        print(f"\n📋 SAMPLE UPDATED COUNTRIES:")
        cursor.execute("""
            SELECT name, population 
            FROM countries_temporal 
            WHERE year = 2024 AND population IS NOT NULL 
            AND name IN ('Faroe Islands', 'Greenland', 'Puerto Rico', 'Guam', 'American Samoa')
            ORDER BY population DESC
        """)
        
        for name, pop in cursor.fetchall():
            print(f"   {name}: {pop:,}")
        
        conn.close()
        
        print(f"\n✅ Successfully updated missing 2024 population data!")
        
    except Exception as e:
        logger.error(f"Error updating missing 2024 populations: {e}")
        raise

if __name__ == "__main__":
    update_missing_2024_populations() 