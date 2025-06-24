#!/usr/bin/env python3
"""
Update 2024 population data in the temporal geography database using CIA World Factbook 2024 estimates.
"""

import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CIA World Factbook 2024 population estimates
POPULATION_2024 = {
    'China': 1416043270,
    'India': 1409128296,
    'United States': 341963408,
    'Indonesia': 281562465,
    'Pakistan': 252363571,
    'Nigeria': 236747130,
    'Brazil': 220051512,
    'Bangladesh': 168697184,
    'Russia': 140820810,
    'Mexico': 130739927,
    'Japan': 123201945,
    'Ethiopia': 118550298,
    'Philippines': 118277063,
    'Congo, Democratic Republic of the': 115403027,
    'Egypt': 111247248,
    'Vietnam': 105758975,
    'Iran': 88386937,
    'Turkey': 84119531,
    'Germany': 84119100,
    'Thailand': 69920998,
    'United Kingdom': 68459055,
    'France': 68374591,
    'Tanzania': 67462121,
    'Italy': 60964931,
    'South Africa': 60442647,
    'Kenya': 58246378,
    'Myanmar': 57527139,
    'South Korea': 52081799,
    'Sudan': 50467278,
    'Colombia': 49588357,
    'Uganda': 49283041,
    'Spain': 47280433,
    'Algeria': 47022473,
    'Argentina': 46994384,
    'Iraq': 42083436,
    'Afghanistan': 40121552,
    'Canada': 38794813,
    'Poland': 38746310,
    'Morocco': 37387585,
    'Angola': 37202061,
    'Saudi Arabia': 36544431,
    'Uzbekistan': 36520593,
    'Ukraine': 35661826,
    'Ghana': 34589092,
    'Malaysia': 34564810,
    'Mozambique': 33350954,
    'Peru': 32600249,
    'Yemen': 32140443,
    'Venezuela': 31250306,
    'Nepal': 31122387,
    'Cameroon': 30966105,
    'Ivory Coast': 29981758,
    'Madagascar': 29452714,
    'Australia': 26768598,
    'Niger': 26342784,
    'North Korea': 26298666,
    'Syria': 23865423,
    'Taiwan': 23595274,
    'Burkina Faso': 23042199,
    'Mali': 21990607,
    'Sri Lanka': 21982608,
    'Malawi': 21763309,
    'Zambia': 20799116,
    'Kazakhstan': 20260006,
    'Chad': 19093595,
    'Senegal': 18847519,
    'Chile': 18664652,
    'Ecuador': 18309984,
    'Guatemala': 18255216,
    'Romania': 18148155,
    'Netherlands': 17772378,
    'Zimbabwe': 17150352,
    'Cambodia': 17063669,
    'Benin': 14697052,
    'Guinea': 13986179,
    'Rwanda': 13623302,
    'Burundi': 13590102,
    'Somalia': 13017273,
    'South Sudan': 12703714,
    'Bolivia': 12311974,
    'Tunisia': 12048847,
    'Belgium': 11977634,
    'Haiti': 11753943,
    'Jordan': 11174024,
    'Cuba': 10966038,
    'Czech Republic': 10837890,
    'Dominican Republic': 10815857,
    'Azerbaijan': 10650239,
    'Sweden': 10589835,
    'Greece': 10461091,
    'Tajikistan': 10394063,
    'Portugal': 10207177,
    'Papua New Guinea': 10046233,
    'United Arab Emirates': 10032213,
    'Hungary': 9855745,
    'Honduras': 9529188,
    'Belarus': 9501451,
    'Israel': 9402617,
    'Sierra Leone': 9121049,
    'Austria': 8967982,
    'Togo': 8917994,
    'Switzerland': 8860574,
    'Laos': 7953556,
    'Paraguay': 7522549,
    'Libya': 7361263,
    'Hong Kong': 7297821,
    'Bulgaria': 6782659,
    'Nicaragua': 6676948,
    'Serbia': 6652212,
    'El Salvador': 6628702,
    'Eritrea': 6343956,
    'Kyrgyzstan': 6172101,
    'Republic of the Congo': 6097665,
    'Singapore': 6028459,
    'Denmark': 5973136,
    'Turkmenistan': 5744151,
    'Central African Republic': 5650957,
    'Finland': 5626414,
    'Slovakia': 5563649,
    'Norway': 5509733,
    'Liberia': 5437249,
    'Lebanon': 5364482,
    'Costa Rica': 5265575,
    'Ireland': 5233461,
    'New Zealand': 5161211,
    'Georgia': 4900961,
    'Panama': 4470241,
    'Mauritania': 4328040,
    'Croatia': 4150116,
    'Oman': 3901992,
    'Bosnia and Herzegovina': 3798671,
    'Moldova': 3599528,
    'Uruguay': 3425330,
    'Mongolia': 3281676,
    'Kuwait': 3138355,
    'Albania': 3107100,
    'Puerto Rico': 3019450,
    'Armenia': 2976765,
    'Jamaica': 2823713,
    'Namibia': 2803660,
    'Lithuania': 2628186,
    'Qatar': 2552088,
    'Gambia': 2523327,
    'Gabon': 2455105,
    'Botswana': 2450668,
    'Lesotho': 2227548,
    'North Macedonia': 2135622,
    'Guinea-Bissau': 2132325,
    'Slovenia': 2097893,
    'Kosovo': 1977093,
    'Latvia': 1801246,
    'Equatorial Guinea': 1795834,
    'Bahrain': 1566888,
    'East Timor': 1506909,
    'Trinidad and Tobago': 1408966,
    'Cyprus': 1320525,
    'Mauritius': 1310504,
    'Estonia': 1193791,
    'Eswatini': 1138089,
    'Djibouti': 994974,
    'Fiji': 951611,
    'Comoros': 900141,
    'Bhutan': 884546,
    'Guyana': 794099,
    'Solomon Islands': 726799,
    'Luxembourg': 671254,
    'Suriname': 646758,
    'Cape Verde': 611014,
    'Montenegro': 599849,
    'Brunei': 491900,
    'Malta': 469730,
    'Belize': 415789,
    'Bahamas': 410862,
    'Maldives': 388858,
    'Iceland': 364036,
    'Vanuatu': 318007,
    'Barbados': 304139,
    'Sao Tome and Principe': 223561,
    'Samoa': 208853,
    'Saint Lucia': 168038,
    'Kiribati': 116545,
    'Grenada': 114621,
    'Tonga': 104889,
    'Antigua and Barbuda': 102634,
    'Saint Vincent and the Grenadines': 100647,
    'Micronesia': 99603,
    'Seychelles': 98187,
    'Andorra': 85370,
    'Marshall Islands': 82011,
    'Dominica': 74661,
    'Saint Kitts and Nevis': 55133,
    'Liechtenstein': 40272,
    'San Marino': 35095,
    'Monaco': 31813,
    'Palau': 21864,
    'Nauru': 9892,
    'Tuvalu': 11733,
    'Vatican City': 1000
}

def update_2024_populations():
    """Update 2024 population data in the temporal database."""
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        logger.info("🔄 Starting 2024 population data update...")
        
        # Update countries with 2024 population data
        updated_count = 0
        not_found_count = 0
        
        for country_name, population in POPULATION_2024.items():
            # Try to find and update the country
            cursor.execute("""
                UPDATE countries_temporal 
                SET population = ? 
                WHERE name = ? AND year = 2024
            """, (population, country_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                logger.info(f"✅ Updated {country_name}: {population:,}")
            else:
                # Try alternative names
                alt_names = {
                    'United States': 'United States of America',
                    'Myanmar': 'Burma',
                    'Congo, Democratic Republic of the': 'Democratic Republic of the Congo',
                    'Ivory Coast': 'Cote d\'Ivoire',
                    'Czech Republic': 'Czechia',
                    'Republic of the Congo': 'Congo',
                    'East Timor': 'Timor-Leste',
                    'Cape Verde': 'Cabo Verde',
                    'Vatican City': 'Holy See'
                }
                
                alt_name = alt_names.get(country_name)
                if alt_name:
                    cursor.execute("""
                        UPDATE countries_temporal 
                        SET population = ? 
                        WHERE name = ? AND year = 2024
                    """, (population, alt_name))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        logger.info(f"✅ Updated {alt_name} (alt name for {country_name}): {population:,}")
                    else:
                        not_found_count += 1
                        logger.warning(f"❌ Country not found: {country_name} (tried {alt_name})")
                else:
                    not_found_count += 1
                    logger.warning(f"❌ Country not found: {country_name}")
        
        # Commit changes
        conn.commit()
        
        # Verify results
        cursor.execute("""
            SELECT COUNT(*) FROM countries_temporal 
            WHERE year = 2024 AND population IS NOT NULL AND population > 0
        """)
        total_with_population = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM countries_temporal WHERE year = 2024")
        total_countries = cursor.fetchone()[0]
        
        logger.info(f"\n📊 2024 Population Update Summary:")
        logger.info(f"   • Successfully updated: {updated_count} countries")
        logger.info(f"   • Not found in database: {not_found_count} countries")
        logger.info(f"   • Total countries with 2024 population: {total_with_population}")
        logger.info(f"   • Total countries in 2024: {total_countries}")
        
        # Show top 10 most populous countries for 2024
        cursor.execute("""
            SELECT name, population 
            FROM countries_temporal 
            WHERE year = 2024 AND population IS NOT NULL 
            ORDER BY population DESC 
            LIMIT 10
        """)
        
        top_countries = cursor.fetchall()
        logger.info(f"\n🏆 Top 10 Most Populous Countries in 2024:")
        for i, (name, pop) in enumerate(top_countries, 1):
            logger.info(f"   {i:2d}. {name}: {pop:,}")
        
        conn.close()
        logger.info("\n✅ 2024 population update completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error updating 2024 populations: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_2024_populations() 