#!/usr/bin/env python3
"""
Update 2023 population data in the temporal geography database using CIA World Factbook 2023 estimates.
"""

import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CIA World Factbook 2023 population estimates
POPULATION_2023 = {
    'China': 1412175000,
    'India': 1393409038,
    'United States': 339996563,
    'Indonesia': 277534122,
    'Pakistan': 242923845,
    'Nigeria': 225082083,
    'Brazil': 217240060,
    'Bangladesh': 167885689,
    'Russia': 142320790,
    'Mexico': 129875529,
    'Japan': 124687293,
    'Ethiopia': 116462712,
    'Philippines': 115559009,
    'Congo, Democratic Republic of the': 108407721,
    'Egypt': 107770524,
    'Vietnam': 98858950,
    'Iran': 86758304,
    'Germany': 84316622,
    'Turkey': 82319724,
    'Thailand': 69950850,
    'United Kingdom': 67736802,
    'Tanzania': 65497748,
    'France': 68521974,
    'Italy': 58940425,
    'South Africa': 60756135,
    'Myanmar': 55227143,
    'Kenya': 55100586,
    'South Korea': 51815810,
    'Colombia': 52085168,
    'Spain': 47519628,
    'Uganda': 48582334,
    'Argentina': 46245668,
    'Algeria': 45350148,
    'Sudan': 48109006,
    'Ukraine': 43306477,
    'Iraq': 41179350,
    'Afghanistan': 39232003,
    'Poland': 38093101,
    'Canada': 38781291,
    'Morocco': 37457971,
    'Saudi Arabia': 35844909,
    'Uzbekistan': 30842796,
    'Peru': 33715471,
    'Angola': 35588987,
    'Malaysia': 33871648,
    'Mozambique': 33089461,
    'Ghana': 33475870,
    'Yemen': 31154867,
    'Nepal': 30896590,
    'Venezuela': 28838499,
    'Madagascar': 28915653,
    'Cameroon': 28524175,
    'Ivory Coast': 28088455,
    'North Korea': 25955138,
    'Australia': 26141369,
    'Niger': 26207977,
    'Sri Lanka': 22181000,
    'Burkina Faso': 22673762,
    'Mali': 21904983,
    'Romania': 18326327,
    'Malawi': 20308502,
    'Chile': 19493184,
    'Kazakhstan': 19606633,
    'Zambia': 20017675,
    'Guatemala': 18092026,
    'Ecuador': 18190484,
    'Syria': 19454263,
    'Netherlands': 17564014,
    'Senegal': 17653671,
    'Cambodia': 16944826,
    'Chad': 17723315,
    'Somalia': 17065581,
    'Zimbabwe': 15993524,
    'Guinea': 13865691,
    'Rwanda': 13776698,
    'Benin': 13301694,
    'Burundi': 12889576,
    'Tunisia': 11976182,
    'Bolivia': 12186079,
    'Belgium': 11720716,
    'Haiti': 11724763,
    'Cuba': 11317505,
    'South Sudan': 11088796,
    'Dominican Republic': 11117873,
    'Czech Republic': 10493986,
    'Greece': 10432481,
    'Jordan': 10909567,
    'Portugal': 10247605,
    'Azerbaijan': 10358074,
    'Sweden': 10536632,
    'Honduras': 10278345,
    'United Arab Emirates': 9516871,
    'Hungary': 9676135,
    'Tajikistan': 9750065,
    'Belarus': 9432800,
    'Austria': 8939617,
    'Papua New Guinea': 9292169,
    'Serbia': 8697550,
    'Israel': 9038000,
    'Switzerland': 8796669,
    'Togo': 8644829,
    'Sierra Leone': 8605718,
    'Hong Kong': 7494336,
    'Laos': 7529475,
    'Paraguay': 7272639,
    'Bulgaria': 6687717,
    'Libya': 6812341,
    'Lebanon': 5489739,
    'Nicaragua': 6850540,
    'Kyrgyzstan': 6735347,
    'El Salvador': 6364943,
    'Turkmenistan': 6031187,
    'Singapore': 5975689,
    'Denmark': 5910913,
    'Finland': 5545475,
    'Congo': 5797805,
    'Slovakia': 5428704,
    'Norway': 5474360,
    'Oman': 5323993,
    'State of Palestine': 5250072,
    'Costa Rica': 5180829,
    'Liberia': 5302681,
    'Ireland': 5020199,
    'Central African Republic': 5357744,
    'New Zealand': 5228100,
    'Mauritania': 4736139,
    'Panama': 4351267,
    'Kuwait': 4310108,
    'Croatia': 3853200,
    'Moldova': 2573928,
    'Georgia': 3728282,
    'Eritrea': 3748901,
    'Uruguay': 3423108,
    'Bosnia and Herzegovina': 3164253,
    'Mongolia': 3398366,
    'Armenia': 2777970,
    'Jamaica': 2825544,
    'Qatar': 2695122,
    'Albania': 2832439,
    'Puerto Rico': 3252407,
    'Lithuania': 2718352,
    'Namibia': 2604172,
    'Gambia': 2639916,
    'Botswana': 2417596,
    'Gabon': 2388992,
    'Lesotho': 2142252,
    'North Macedonia': 2085679,
    'Slovenia': 2119675,
    'Guinea-Bissau': 2105566,
    'Latvia': 1883008,
    'Bahrain': 1748296,
    'Equatorial Guinea': 1496662,
    'Trinidad and Tobago': 1405646,
    'Estonia': 1322765,
    'East Timor': 1360596,
    'Mauritius': 1299469,
    'Cyprus': 1244188,
    'Eswatini': 1201670,
    'Djibouti': 1120849,
    'Fiji': 924610,
    'Reunion': 868846,
    'Comoros': 888451,
    'Guyana': 804567,
    'Bhutan': 782318,
    'Solomon Islands': 740424,
    'Macao': 695168,
    'Montenegro': 627082,
    'Western Sahara': 652271,
    'Luxembourg': 640064,
    'Suriname': 612985,
    'Cape Verde': 598682,
    'Maldives': 540985,
    'Malta': 535064,
    'Brunei': 449002,
    'Guadeloupe': 395700,
    'Belize': 405272,
    'Bahamas': 412623,
    'Martinique': 366981,
    'Iceland': 375318,
    'Vanuatu': 334506,
    'French Polynesia': 306279,
    'Barbados': 281635,
    'New Caledonia': 290915,
    'French Guiana': 312155,
    'Mayotte': 320081,
    'Sao Tome and Principe': 227679,
    'Samoa': 205557,
    'Saint Lucia': 180251,
    'Channel Islands': 176463,
    'Guam': 172952,
    'Curacao': 191163,
    'Kiribati': 131232,
    'Micronesia': 113131,
    'Grenada': 124610,
    'Saint Vincent and the Grenadines': 103948,
    'Aruba': 106445,
    'Tonga': 108020,
    'United States Virgin Islands': 99465,
    'Seychelles': 107660,
    'Antigua and Barbuda': 93219,
    'Isle of Man': 84710,
    'Andorra': 79824,
    'Dominica': 73897,
    'Cayman Islands': 69310,
    'Bermuda': 64069,
    'Marshall Islands': 42418,
    'Northern Mariana Islands': 49796,
    'Greenland': 56661,
    'American Samoa': 45443,
    'Saint Kitts and Nevis': 47755,
    'Faroe Islands': 53270,
    'Sint Maarten': 44222,
    'Monaco': 36686,
    'Turks and Caicos Islands': 46062,
    'Saint Martin': 32358,
    'Liechtenstein': 39327,
    'San Marino': 33644,
    'Gibraltar': 29461,
    'British Virgin Islands': 31122,
    'Cook Islands': 17565,
    'Palau': 18055,
    'Nauru': 12668,
    'Wallis and Futuna': 11369,
    'Anguilla': 15857,
    'Tuvalu': 11204,
    'Saint Barthelemy': 7122,
    'Saint Helena': 7925,
    'Saint Pierre and Miquelon': 5840,
    'Montserrat': 4649,
    'Falkland Islands': 3198,
    'Norfolk Island': 1748,
    'Christmas Island': 1692,
    'Tokelau': 1893,
    'Niue': 1934,
    'Vatican City': 825,
    'Cocos Islands': 596,
    'Pitcairn Islands': 50,
    # Uninhabited territories
    'Antarctica': 0,
    'Bouvet Island': 0,
    'French Southern Territories': 0,
    'Heard Island and McDonald Islands': 0,
    'South Georgia and the South Sandwich Islands': 0,
    'British Indian Ocean Territory': 0,
    'United States Minor Outlying Islands': 0
}

def update_2023_populations():
    """Update 2023 population data in the temporal database."""
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        logger.info("Starting 2023 population data update...")
        
        updated_count = 0
        not_found_count = 0
        not_found_countries = []
        
        for country_name, population in POPULATION_2023.items():
            # Try to find and update the country
            cursor.execute("""
                UPDATE countries_temporal 
                SET population = ? 
                WHERE year = 2023 AND name = ?
            """, (population, country_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                logger.info(f"Updated {country_name}: {population:,}")
            else:
                # Try alternative names
                alternatives = get_alternative_names(country_name)
                found = False
                for alt_name in alternatives:
                    cursor.execute("""
                        UPDATE countries_temporal 
                        SET population = ? 
                        WHERE year = 2023 AND name = ?
                    """, (population, alt_name))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        logger.info(f"Updated {alt_name} (searched as {country_name}): {population:,}")
                        found = True
                        break
                
                if not found:
                    not_found_count += 1
                    not_found_countries.append(country_name)
                    logger.warning(f"Country not found: {country_name}")
        
        # Commit changes
        conn.commit()
        
        # Print summary
        logger.info(f"\n2023 Population Update Summary:")
        logger.info(f"Successfully updated: {updated_count} countries")
        logger.info(f"Not found: {not_found_count} countries")
        
        if not_found_countries:
            logger.info(f"Countries not found: {', '.join(not_found_countries)}")
        
        # Show total population for 2023
        cursor.execute("""
            SELECT COUNT(*) as total_countries,
                   COUNT(CASE WHEN population IS NOT NULL AND population > 0 THEN 1 END) as with_population,
                   SUM(CASE WHEN population IS NOT NULL THEN population ELSE 0 END) as total_population
            FROM countries_temporal 
            WHERE year = 2023
        """)
        
        result = cursor.fetchone()
        total_countries, with_population, total_population = result
        
        logger.info(f"\n2023 Database Status:")
        logger.info(f"Total countries: {total_countries}")
        logger.info(f"Countries with population: {with_population}")
        logger.info(f"Coverage: {(with_population/total_countries)*100:.1f}%")
        logger.info(f"Total world population: {total_population:,}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error updating 2023 populations: {e}")
        raise

def get_alternative_names(country_name):
    """Get alternative names for countries that might be stored differently."""
    alternatives = {
        'United States': ['United States of America', 'USA'],
        'United Kingdom': ['United Kingdom of Great Britain and Northern Ireland', 'UK'],
        'Congo, Democratic Republic of the': ['Democratic Republic of the Congo', 'Congo (Democratic Republic)', 'DRC'],
        'Congo': ['Republic of the Congo', 'Congo (Republic)'],
        'North Korea': ['Democratic People\'s Republic of Korea', 'Korea, North'],
        'South Korea': ['Republic of Korea', 'Korea, South'],
        'Russia': ['Russian Federation'],
        'Iran': ['Islamic Republic of Iran'],
        'Syria': ['Syrian Arab Republic'],
        'Venezuela': ['Bolivarian Republic of Venezuela'],
        'Bolivia': ['Plurinational State of Bolivia'],
        'Tanzania': ['United Republic of Tanzania'],
        'Moldova': ['Republic of Moldova'],
        'North Macedonia': ['Macedonia', 'Former Yugoslav Republic of Macedonia'],
        'Eswatini': ['Swaziland'],
        'East Timor': ['Timor-Leste'],
        'State of Palestine': ['Palestine'],
        'Vatican City': ['Holy See'],
        'Ivory Coast': ['Cote d\'Ivoire'],
        'Cape Verde': ['Cabo Verde'],
        'Myanmar': ['Burma'],
        'Czechia': ['Czech Republic'],
        'Channel Islands': ['Jersey', 'Guernsey']
    }
    
    return alternatives.get(country_name, [])

if __name__ == "__main__":
    update_2023_populations() 