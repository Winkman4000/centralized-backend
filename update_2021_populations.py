#!/usr/bin/env python3
"""
Update 2021 population data in the temporal geography database using CIA World Factbook 2021 estimates.
"""

import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CIA World Factbook 2021 population estimates
POPULATION_2021 = {
    'China': 1402112000,
    'India': 1366417754,
    'United States': 334805269,
    'Indonesia': 273523615,
    'Pakistan': 233500636,
    'Nigeria': 211400708,
    'Brazil': 213993437,
    'Bangladesh': 164689383,
    'Russia': 142320790,
    'Mexico': 126014024,
    'Japan': 125507472,
    'Ethiopia': 112078730,
    'Philippines': 109581078,
    'Congo, Democratic Republic of the': 101780263,
    'Egypt': 104258327,
    'Vietnam': 97338579,
    'Iran': 84923314,
    'Germany': 80159662,
    'Turkey': 84339067,
    'Thailand': 69037513,
    'United Kingdom': 67886011,
    'Tanzania': 61498437,
    'France': 67848156,
    'Italy': 60461826,
    'South Africa': 59308690,
    'Myanmar': 54409800,
    'Kenya': 53771296,
    'South Korea': 51269185,
    'Colombia': 50882891,
    'Spain': 46754778,
    'Uganda': 45741007,
    'Argentina': 45195774,
    'Algeria': 43851044,
    'Sudan': 45561556,
    'Ukraine': 43733762,
    'Iraq': 40222493,
    'Afghanistan': 36643815,
    'Poland': 37846611,
    'Canada': 37742154,
    'Morocco': 36471769,
    'Saudi Arabia': 34813871,
    'Uzbekistan': 30243200,
    'Peru': 32971854,
    'Angola': 32866272,
    'Malaysia': 32365999,
    'Mozambique': 31255435,
    'Ghana': 31072940,
    'Yemen': 29825964,
    'Nepal': 29136808,
    'Venezuela': 28435940,
    'Madagascar': 27691018,
    'Cameroon': 27222181,
    'Ivory Coast': 26378274,
    'North Korea': 25778816,
    'Australia': 25499884,
    'Niger': 24206644,
    'Sri Lanka': 21413249,
    'Burkina Faso': 21497096,
    'Mali': 20250833,
    'Romania': 19237691,
    'Malawi': 19129952,
    'Chile': 18952038,
    'Kazakhstan': 19002586,
    'Zambia': 18383955,
    'Guatemala': 17915568,
    'Ecuador': 17643054,
    'Syria': 18275702,
    'Netherlands': 17134872,
    'Senegal': 16743927,
    'Cambodia': 16718965,
    'Chad': 16425864,
    'Somalia': 15893222,
    'Zimbabwe': 14862924,
    'Guinea': 13132795,
    'Rwanda': 12952218,
    'Benin': 12123200,
    'Burundi': 11890784,
    'Tunisia': 11818619,
    'Bolivia': 11673021,
    'Belgium': 11589623,
    'Haiti': 11402528,
    'Cuba': 11326616,
    'South Sudan': 11193725,
    'Dominican Republic': 10847910,
    'Czech Republic': 10708981,
    'Greece': 10423054,
    'Jordan': 10203134,
    'Portugal': 10196709,
    'Azerbaijan': 10139177,
    'Sweden': 10099265,
    'Honduras': 9904607,
    'United Arab Emirates': 9890402,
    'Hungary': 9660351,
    'Tajikistan': 9537645,
    'Belarus': 9449323,
    'Austria': 9006398,
    'Papua New Guinea': 8947024,
    'Serbia': 8737371,
    'Israel': 8655535,
    'Switzerland': 8654622,
    'Togo': 8278724,
    'Sierra Leone': 8051641,
    'Hong Kong': 7496981,
    'Laos': 7275560,
    'Paraguay': 7132538,
    'Bulgaria': 6948445,
    'Libya': 6871292,
    'Lebanon': 6825445,
    'Nicaragua': 6624554,
    'Kyrgyzstan': 6524195,
    'El Salvador': 6486205,
    'Turkmenistan': 6031187,
    'Singapore': 5850342,
    'Denmark': 5792202,
    'Finland': 5540720,
    'Congo': 5518087,
    'Slovakia': 5459642,
    'Norway': 5421241,
    'Oman': 5106626,
    'State of Palestine': 5101414,
    'Costa Rica': 5094118,
    'Liberia': 5057681,
    'Ireland': 4937786,
    'Central African Republic': 4829767,
    'New Zealand': 4822233,
    'Mauritania': 4649658,
    'Panama': 4314767,
    'Kuwait': 4270571,
    'Croatia': 4105267,
    'Moldova': 4033963,
    'Georgia': 3989167,
    'Eritrea': 3546421,
    'Uruguay': 3473730,
    'Bosnia and Herzegovina': 3280819,
    'Mongolia': 3278290,
    'Armenia': 2963243,
    'Jamaica': 2961167,
    'Qatar': 2881053,
    'Albania': 2877797,
    'Puerto Rico': 2860853,
    'Lithuania': 2722289,
    'Namibia': 2540905,
    'Gambia': 2416668,
    'Botswana': 2351627,
    'Gabon': 2225734,
    'Lesotho': 2142249,
    'North Macedonia': 2083374,
    'Slovenia': 2078938,
    'Guinea-Bissau': 1968001,
    'Latvia': 1886198,
    'Bahrain': 1701575,
    'Equatorial Guinea': 1402985,
    'Trinidad and Tobago': 1399488,
    'Estonia': 1326535,
    'East Timor': 1318445,
    'Mauritius': 1271768,
    'Cyprus': 1207359,
    'Eswatini': 1160164,
    'Djibouti': 988000,
    'Fiji': 896445,
    'Reunion': 895312,
    'Comoros': 869601,
    'Guyana': 786552,
    'Bhutan': 771608,
    'Solomon Islands': 686884,
    'Macao': 649335,
    'Montenegro': 628066,
    'Western Sahara': 597339,
    'Luxembourg': 625978,
    'Suriname': 586632,
    'Cape Verde': 555987,
    'Maldives': 540544,
    'Malta': 441543,
    'Brunei': 437479,
    'Guadeloupe': 400124,
    'Belize': 397628,
    'Bahamas': 393244,
    'Martinique': 375265,
    'Iceland': 341243,
    'Vanuatu': 307145,
    'French Polynesia': 280908,
    'Barbados': 287375,
    'New Caledonia': 285498,
    'French Guiana': 298682,
    'Mayotte': 272815,
    'Sao Tome and Principe': 219159,
    'Samoa': 198414,
    'Saint Lucia': 183627,
    'Channel Islands': 173863,
    'Guam': 168775,
    'Curacao': 164093,
    'Kiribati': 119449,
    'Micronesia': 115023,
    'Grenada': 112523,
    'Saint Vincent and the Grenadines': 110940,
    'Aruba': 106766,
    'Tonga': 105695,
    'United States Virgin Islands': 104425,
    'Seychelles': 98347,
    'Antigua and Barbuda': 97929,
    'Isle of Man': 85033,
    'Andorra': 77265,
    'Dominica': 71986,
    'Cayman Islands': 61944,
    'Bermuda': 62278,
    'Marshall Islands': 59190,
    'Northern Mariana Islands': 57559,
    'Greenland': 56770,
    'American Samoa': 55191,
    'Saint Kitts and Nevis': 53199,
    'Faroe Islands': 48863,
    'Sint Maarten': 42876,
    'Monaco': 39242,
    'Turks and Caicos Islands': 38717,
    'Saint Martin': 38666,
    'Liechtenstein': 38128,
    'San Marino': 33931,
    'Gibraltar': 33691,
    'British Virgin Islands': 30231,
    'Cook Islands': 17564,
    'Palau': 18094,
    'Nauru': 10824,
    'Wallis and Futuna': 11239,
    'Anguilla': 15003,
    'Tuvalu': 11792,
    'Saint Barthelemy': 9877,
    'Saint Helena': 7862,
    'Saint Pierre and Miquelon': 5794,
    'Montserrat': 5177,
    'Falkland Islands': 3480,
    'Norfolk Island': 1748,
    'Christmas Island': 1843,
    'Tokelau': 1357,
    'Niue': 1626,
    'Vatican City': 801,
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

def update_2021_populations():
    """Update 2021 population data in the temporal database."""
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        logger.info("Starting 2021 population data update...")
        
        updated_count = 0
        not_found_count = 0
        not_found_countries = []
        
        for country_name, population in POPULATION_2021.items():
            # Try to find and update the country
            cursor.execute("""
                UPDATE countries_temporal 
                SET population = ? 
                WHERE year = 2021 AND name = ?
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
                        WHERE year = 2021 AND name = ?
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
        logger.info(f"\n2021 Population Update Summary:")
        logger.info(f"Successfully updated: {updated_count} countries")
        logger.info(f"Not found: {not_found_count} countries")
        
        if not_found_countries:
            logger.info(f"Countries not found: {', '.join(not_found_countries)}")
        
        # Show total population for 2021
        cursor.execute("""
            SELECT COUNT(*) as total_countries,
                   COUNT(CASE WHEN population IS NOT NULL AND population > 0 THEN 1 END) as with_population,
                   SUM(CASE WHEN population IS NOT NULL THEN population ELSE 0 END) as total_population
            FROM countries_temporal 
            WHERE year = 2021
        """)
        
        result = cursor.fetchone()
        total_countries, with_population, total_population = result
        
        logger.info(f"\n2021 Database Status:")
        logger.info(f"Total countries: {total_countries}")
        logger.info(f"Countries with population: {with_population}")
        logger.info(f"Coverage: {(with_population/total_countries)*100:.1f}%")
        logger.info(f"Total world population: {total_population:,}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error updating 2021 populations: {e}")
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
    update_2021_populations() 