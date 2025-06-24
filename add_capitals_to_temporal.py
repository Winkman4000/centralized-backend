#!/usr/bin/env python3
"""
Add capital cities to the temporal geography database.
Based on research, no countries have changed their capitals in the last 5 years (2020-2025).
The most recent capital change was Myanmar in 2005 (Yangon to Naypyidaw).
"""

import sqlite3
import sys

# Comprehensive capital city data for all countries
# Based on research: no capital changes occurred 2020-2025
CAPITALS_DATA = {
    # Major countries
    "China": "Beijing",
    "India": "New Delhi", 
    "United States": "Washington, D.C.",
    "Indonesia": "Jakarta",  # Note: Nusantara planned but not yet moved
    "Pakistan": "Islamabad",
    "Brazil": "Brasília",
    "Nigeria": "Abuja",
    "Bangladesh": "Dhaka",
    "Russia": "Moscow",
    "Mexico": "Mexico City",
    "Japan": "Tokyo",
    "Ethiopia": "Addis Ababa",
    "Philippines": "Manila",
    "Egypt": "Cairo",
    "Vietnam": "Hanoi",
    "DR Congo": "Kinshasa",
    "Turkey": "Ankara",
    "Iran": "Tehran",
    "Germany": "Berlin",
    "Thailand": "Bangkok",
    "United Kingdom": "London",
    "France": "Paris",
    "Italy": "Rome",
    "Tanzania": "Dodoma",
    "South Africa": "Pretoria",  # Executive capital
    "Myanmar": "Naypyidaw",  # Changed from Yangon in 2005
    "Kenya": "Nairobi",
    "Uganda": "Kampala",
    "Algeria": "Algiers",
    "Sudan": "Khartoum",
    "Ukraine": "Kyiv",
    "Iraq": "Baghdad",
    "Afghanistan": "Kabul",
    "Poland": "Warsaw",
    "Canada": "Ottawa",
    "Morocco": "Rabat",
    "Saudi Arabia": "Riyadh",
    "Uzbekistan": "Tashkent",
    "Peru": "Lima",
    "Angola": "Luanda",
    "Malaysia": "Kuala Lumpur",
    "Mozambique": "Maputo",
    "Ghana": "Accra",
    "Yemen": "Sanaa",
    "Nepal": "Kathmandu",
    "Venezuela": "Caracas",
    "Madagascar": "Antananarivo",
    "Cameroon": "Yaoundé",
    "Ivory Coast": "Yamoussoukro",  # Official capital (Abidjan is economic)
    "North Korea": "Pyongyang",
    "Australia": "Canberra",
    "Syria": "Damascus",
    "Mali": "Bamako",
    "Burkina Faso": "Ouagadougou",
    "Sri Lanka": "Colombo",  # Executive capital
    "Chile": "Santiago",
    "Malawi": "Lilongwe",
    "Zambia": "Lusaka",
    "Romania": "Bucharest",
    "Kazakhstan": "Astana",  # Changed from Almaty in 1997
    "Somalia": "Mogadishu",
    "Guatemala": "Guatemala City",
    "Senegal": "Dakar",
    "Netherlands": "Amsterdam",
    "Ecuador": "Quito",
    "Cambodia": "Phnom Penh",
    "Chad": "N'Djamena",
    "Guinea": "Conakry",
    "Rwanda": "Kigali",
    "Benin": "Porto-Novo",
    "Tunisia": "Tunis",
    "Burundi": "Gitega",  # Changed from Bujumbura in 2019
    "Bolivia": "Sucre",  # Constitutional capital (La Paz is administrative)
    "Belgium": "Brussels",
    "Haiti": "Port-au-Prince",
    "Cuba": "Havana",
    "South Sudan": "Juba",
    "Dominican Republic": "Santo Domingo",
    "Czech Republic": "Prague",
    "Greece": "Athens",
    "Jordan": "Amman",
    "Portugal": "Lisbon",
    "Azerbaijan": "Baku",
    "Sweden": "Stockholm",
    "Honduras": "Tegucigalpa",
    "United Arab Emirates": "Abu Dhabi",
    "Hungary": "Budapest",
    "Belarus": "Minsk",
    "Tajikistan": "Dushanbe",
    "Austria": "Vienna",
    "Papua New Guinea": "Port Moresby",
    "Serbia": "Belgrade",
    "Israel": "Jerusalem",
    "Switzerland": "Bern",
    "Togo": "Lomé",
    "Sierra Leone": "Freetown",
    "Laos": "Vientiane",
    "Paraguay": "Asunción",
    "Libya": "Tripoli",
    "Lebanon": "Beirut",
    "Nicaragua": "Managua",
    "Kyrgyzstan": "Bishkek",
    "El Salvador": "San Salvador",
    "Turkmenistan": "Ashgabat",
    "Singapore": "Singapore",
    "Denmark": "Copenhagen",
    "Finland": "Helsinki",
    "Slovakia": "Bratislava",
    "Norway": "Oslo",
    "Oman": "Muscat",
    "Costa Rica": "San José",
    "Liberia": "Monrovia",
    "Ireland": "Dublin",
    "Central African Republic": "Bangui",
    "New Zealand": "Wellington",
    "Mauritania": "Nouakchott",
    "Panama": "Panama City",
    "Kuwait": "Kuwait City",
    "Croatia": "Zagreb",
    "Moldova": "Chișinău",
    "Georgia": "Tbilisi",
    "Eritrea": "Asmara",
    "Uruguay": "Montevideo",
    "Mongolia": "Ulaanbaatar",
    "Bosnia and Herzegovina": "Sarajevo",
    "Jamaica": "Kingston",
    "Armenia": "Yerevan",
    "Lithuania": "Vilnius",
    "Albania": "Tirana",
    "Qatar": "Doha",
    "Namibia": "Windhoek",
    "Gambia": "Banjul",
    "Botswana": "Gaborone",
    "Gabon": "Libreville",
    "Lesotho": "Maseru",
    "Slovenia": "Ljubljana",
    "North Macedonia": "Skopje",
    "Latvia": "Riga",
    "Bahrain": "Manama",
    "Equatorial Guinea": "Malabo",
    "Trinidad and Tobago": "Port of Spain",
    "Estonia": "Tallinn",
    "Mauritius": "Port Louis",
    "Cyprus": "Nicosia",
    "Eswatini": "Mbabane",  # Administrative capital
    "Djibouti": "Djibouti",
    "Fiji": "Suva",
    "Comoros": "Moroni",
    "Guyana": "Georgetown",
    "Bhutan": "Thimphu",
    "Solomon Islands": "Honiara",
    "Montenegro": "Podgorica",
    "Luxembourg": "Luxembourg",
    "Suriname": "Paramaribo",
    "Cape Verde": "Praia",
    "Micronesia": "Palikir",
    "Malta": "Valletta",
    "Brunei": "Bandar Seri Begawan",
    "Maldives": "Malé",
    "Belize": "Belmopan",
    "Bahamas": "Nassau",
    "Iceland": "Reykjavík",
    "Barbados": "Bridgetown",
    "Samoa": "Apia",
    "Vanuatu": "Port Vila",
    "Saint Lucia": "Castries",
    "Kiribati": "Tarawa",
    "Grenada": "St. George's",
    "Saint Vincent and the Grenadines": "Kingstown",
    "Tonga": "Nuku'alofa",
    "Antigua and Barbuda": "St. John's",
    "Andorra": "Andorra la Vella",
    "Dominica": "Roseau",
    "Saint Kitts and Nevis": "Basseterre",
    "Marshall Islands": "Majuro",
    "Liechtenstein": "Vaduz",
    "Monaco": "Monaco",
    "Nauru": "Yaren",
    "Tuvalu": "Funafuti",
    "San Marino": "San Marino",
    "Palau": "Ngerulmud",
    "Vatican City": "Vatican City",
    
    # Additional countries and territories
    "Taiwan": "Taipei",
    "Kosovo": "Pristina",
    "Western Sahara": "Laayoune",
    "Palestine": "Ramallah",
    "Puerto Rico": "San Juan",
    "Hong Kong": "Hong Kong",
    "Macau": "Macau",
    "Greenland": "Nuuk",
    "Faroe Islands": "Tórshavn",
    "Aruba": "Oranjestad",
    "Curaçao": "Willemstad",
    "Sint Maarten": "Philipsburg",
    "Cayman Islands": "George Town",
    "British Virgin Islands": "Road Town",
    "US Virgin Islands": "Charlotte Amalie",
    "Turks and Caicos": "Cockburn Town",
    "Bermuda": "Hamilton",
    "Anguilla": "The Valley",
    "Montserrat": "Plymouth",
    "Gibraltar": "Gibraltar",
    "Isle of Man": "Douglas",
    "Jersey": "Saint Helier",
    "Guernsey": "Saint Peter Port",
    "Falkland Islands": "Stanley",
    "South Georgia and South Sandwich Islands": "King Edward Point",
    "Saint Helena": "Jamestown",
    "Ascension Island": "Georgetown",
    "Tristan da Cunha": "Edinburgh of the Seven Seas",
    "French Polynesia": "Papeete",
    "New Caledonia": "Nouméa",
    "Wallis and Futuna": "Mata-Utu",
    "French Guiana": "Cayenne",
    "Martinique": "Fort-de-France",
    "Guadeloupe": "Basse-Terre",
    "Mayotte": "Mamoudzou",
    "Réunion": "Saint-Denis",
    "Saint Pierre and Miquelon": "Saint-Pierre",
    "Cook Islands": "Avarua",
    "Niue": "Alofi",
    "Tokelau": "Nukunonu",
    "American Samoa": "Pago Pago",
    "Guam": "Hagåtña",
    "Northern Mariana Islands": "Saipan",
    "Norfolk Island": "Kingston",
    "Christmas Island": "Flying Fish Cove",
    "Cocos Islands": "West Island"
}

def add_capitals_to_temporal_db():
    """Add capital cities to all countries in the temporal database for all years."""
    
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        # First, add capital column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE countries_temporal ADD COLUMN capital TEXT')
            print("✅ Added capital column to countries_temporal table")
        except sqlite3.OperationalError:
            print("📝 Capital column already exists")
        
        # Get all countries from the database
        cursor.execute('SELECT DISTINCT name FROM countries_temporal ORDER BY name')
        db_countries = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(db_countries)} countries in temporal database")
        print(f"📋 Have capital data for {len(CAPITALS_DATA)} countries/territories")
        
        # Update countries with capital data
        updated_count = 0
        missing_capitals = []
        
        for country in db_countries:
            if country in CAPITALS_DATA:
                capital = CAPITALS_DATA[country]
                # Update all years for this country
                cursor.execute('''
                    UPDATE countries_temporal 
                    SET capital = ? 
                    WHERE name = ?
                ''', (capital, country))
                updated_count += 1
                print(f"✅ {country}: {capital}")
            else:
                missing_capitals.append(country)
                print(f"❌ Missing capital for: {country}")
        
        # Show summary
        print(f"\n📈 SUMMARY:")
        print(f"✅ Updated {updated_count} countries with capitals")
        print(f"❌ Missing capitals for {len(missing_capitals)} countries")
        
        if missing_capitals:
            print(f"\n🔍 Countries missing capitals:")
            for country in missing_capitals:
                print(f"   - {country}")
        
        # Verify the updates
        cursor.execute('''
            SELECT year, COUNT(*) as countries_with_capitals
            FROM countries_temporal 
            WHERE capital IS NOT NULL AND capital != ''
            GROUP BY year
            ORDER BY year
        ''')
        
        print(f"\n📊 VERIFICATION - Countries with capitals by year:")
        for row in cursor.fetchall():
            year, count = row
            print(f"   {year}: {count} countries")
        
        # Show some examples
        cursor.execute('''
            SELECT name, capital, year
            FROM countries_temporal 
            WHERE capital IS NOT NULL 
            ORDER BY name, year
            LIMIT 10
        ''')
        
        print(f"\n🔍 SAMPLE DATA:")
        for row in cursor.fetchall():
            name, capital, year = row
            print(f"   {name} ({year}): {capital}")
        
        # Commit changes
        conn.commit()
        print(f"\n💾 Changes committed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🏛️ ADDING CAPITAL CITIES TO TEMPORAL DATABASE")
    print("=" * 60)
    
    success = add_capitals_to_temporal_db()
    
    if success:
        print("\n🎉 Capital cities successfully added to temporal database!")
        print("💡 Note: No countries changed capitals during 2020-2025 period")
        print("📅 Most recent capital change: Myanmar (2005) - Yangon → Naypyidaw")
    else:
        print("\n❌ Failed to add capital cities")
        sys.exit(1) 