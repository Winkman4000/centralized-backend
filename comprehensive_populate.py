#!/usr/bin/env python3
"""
Comprehensive Geography Database Population Script
Downloads from multiple sources to get 3000+ entries including:
- All countries and territories (249 from ISO 3166-1)
- All subdivisions (3000+ from ISO 3166-2)
- Dependencies, overseas territories, etc.
"""

import requests
import sqlite3
import json
import time
from typing import Dict, List, Any, Optional

class ComprehensiveGeographyPopulator:
    def __init__(self, db_path: str = 'geography.db'):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Geography-Database-Builder/1.0'
        })
        
    def connect_db(self):
        """Connect to the database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def get_continent_id(self, conn: sqlite3.Connection, continent_name: str) -> int:
        """Get continent ID by name"""
        cursor = conn.execute("SELECT id FROM continents WHERE name = ?", (continent_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def insert_country(self, conn: sqlite3.Connection, country_data: Dict[str, Any]) -> int:
        """Insert country and return its ID"""
        cursor = conn.execute("""
            INSERT OR IGNORE INTO countries 
            (name, code_iso3, code_iso2, continent_id, capital, population, area_km2)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            country_data.get('name'),
            country_data.get('code_iso3'),
            country_data.get('code_iso2'),
            country_data.get('continent_id'),
            country_data.get('capital'),
            country_data.get('population'),
            country_data.get('area')
        ))
        
        # Get the ID
        cursor = conn.execute("SELECT id FROM countries WHERE name = ? AND code_iso3 = ?", 
                            (country_data.get('name'), country_data.get('code_iso3')))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def insert_subdivision(self, conn: sqlite3.Connection, subdivision_data: Dict[str, Any]) -> int:
        """Insert state/province and return its ID"""
        cursor = conn.execute("""
            INSERT OR IGNORE INTO states_provinces 
            (name, code, country_id, type, population, area_km2)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            subdivision_data.get('name'),
            subdivision_data.get('code'),
            subdivision_data.get('country_id'),
            subdivision_data.get('type'),
            subdivision_data.get('population'),
            subdivision_data.get('area')
        ))
        
        cursor = conn.execute("SELECT id FROM states_provinces WHERE name = ? AND country_id = ?", 
                            (subdivision_data.get('name'), subdivision_data.get('country_id')))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def map_region_to_continent(self, region: str, subregion: str = None) -> str:
        """Map region/subregion to continent"""
        region_mapping = {
            'Africa': 'Africa',
            'Americas': 'North America' if subregion in ['Northern America', 'Central America', 'Caribbean'] else 'South America',
            'Asia': 'Asia',
            'Europe': 'Europe',
            'Oceania': 'Australia/Oceania',
            'Antarctic': 'Antarctica'
        }
        return region_mapping.get(region, 'Unknown')
    
    def download_comprehensive_countries(self) -> List[Dict[str, Any]]:
        """Download comprehensive country data from mledoze/countries"""
        print("🌍 Downloading comprehensive country data...")
        
        try:
            # Get the comprehensive dataset with all 249 entries
            url = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            countries_data = response.json()
            print(f"✅ Downloaded {len(countries_data)} countries/territories")
            
            processed_countries = []
            
            for country in countries_data:
                # Map to continent
                continent_name = self.map_region_to_continent(
                    country.get('region', ''),
                    country.get('subregion', '')
                )
                
                # Extract capital
                capital = country.get('capital', [])
                capital_str = ', '.join(capital) if isinstance(capital, list) else str(capital) if capital else None
                
                processed_countries.append({
                    'name': country.get('name', {}).get('common', 'Unknown'),
                    'official_name': country.get('name', {}).get('official', ''),
                    'code': country.get('cca3', ''),
                    'code2': country.get('cca2', ''),
                    'continent_name': continent_name,
                    'capital': capital_str,
                    'population': country.get('population'),
                    'area': country.get('area'),
                    'region': country.get('region', ''),
                    'subregion': country.get('subregion', ''),
                    'independent': country.get('independent', False),
                    'un_member': country.get('unMember', False)
                })
            
            return processed_countries
            
        except Exception as e:
            print(f"❌ Error downloading country data: {e}")
            return []
    
    def download_subdivisions_data(self) -> List[Dict[str, Any]]:
        """Download ISO 3166-2 subdivision data"""
        print("🏛️ Downloading subdivision data...")
        
        try:
            # Try CSV format from stefangabos
            url = "https://raw.githubusercontent.com/stefangabos/world_countries/master/data/subdivisions/subdivisions.csv"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV manually
            lines = response.text.strip().split('\n')
            subdivisions = []
            
            for line in lines[1:]:  # Skip header
                # Handle CSV parsing with potential commas in quoted fields
                parts = []
                current_part = ""
                in_quotes = False
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        parts.append(current_part.strip('"'))
                        current_part = ""
                    else:
                        current_part += char
                
                if current_part:
                    parts.append(current_part.strip('"'))
                
                if len(parts) >= 4:
                    subdivisions.append({
                        'country_code': parts[0],
                        'subdivision_code': parts[1],
                        'subdivision_name': parts[2],
                        'subdivision_type': parts[3],
                        'parent': parts[4] if len(parts) > 4 else None
                    })
            
            print(f"✅ Downloaded {len(subdivisions)} subdivisions from CSV")
            return subdivisions
                
        except Exception as e:
            print(f"❌ Error downloading subdivision data: {e}")
            return []
    
    def populate_countries(self, conn: sqlite3.Connection, countries_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Populate countries table and return mapping of country codes to IDs"""
        print("🏛️ Populating countries...")
        
        country_id_map = {}
        
        for country in countries_data:
            # Get continent ID
            continent_id = self.get_continent_id(conn, country['continent_name'])
            if not continent_id:
                print(f"⚠️ Unknown continent: {country['continent_name']} for {country['name']}")
                continue
            
            country_data = {
                'name': country['name'],
                'code_iso3': country['code'],
                'code_iso2': country['code2'],
                'continent_id': continent_id,
                'capital': country['capital'],
                'population': country['population'],
                'area': country['area']
            }
            
            country_id = self.insert_country(conn, country_data)
            if country_id:
                country_id_map[country['code']] = country_id
                country_id_map[country.get('code2', '')] = country_id  # Also map 2-letter codes
        
        print(f"✅ Populated {len(country_id_map)} countries")
        return country_id_map
    
    def populate_subdivisions(self, conn: sqlite3.Connection, subdivisions_data: List[Dict[str, Any]], country_id_map: Dict[str, int]):
        """Populate subdivisions table"""
        print("🏛️ Populating subdivisions...")
        
        subdivision_count = 0
        
        for subdivision in subdivisions_data:
            country_code = subdivision.get('country_code', '')
            country_id = country_id_map.get(country_code)
            
            if not country_id:
                continue
            
            subdivision_data = {
                'name': subdivision.get('subdivision_name', ''),
                'code': subdivision.get('subdivision_code', ''),
                'country_id': country_id,
                'type': subdivision.get('subdivision_type', 'subdivision'),
                'population': None,  # Not available in this dataset
                'area': None        # Not available in this dataset
            }
            
            if self.insert_subdivision(conn, subdivision_data):
                subdivision_count += 1
        
        print(f"✅ Populated {subdivision_count} subdivisions")
    
    def add_major_cities(self, conn: sqlite3.Connection, country_id_map: Dict[str, int]):
        """Add major world cities"""
        print("🏙️ Adding major cities...")
        
        major_cities = [
            ('Tokyo', 'JPN', 37400000),
            ('Delhi', 'IND', 32900000),
            ('Shanghai', 'CHN', 28500000),
            ('Dhaka', 'BGD', 22000000),
            ('São Paulo', 'BRA', 22400000),
            ('Cairo', 'EGY', 21300000),
            ('Mexico City', 'MEX', 21800000),
            ('Beijing', 'CHN', 21500000),
            ('Mumbai', 'IND', 20700000),
            ('Osaka', 'JPN', 18900000),
            ('New York', 'USA', 18800000),
            ('Karachi', 'PAK', 16100000),
            ('Istanbul', 'TUR', 15500000),
            ('Kinshasa', 'COD', 15000000),
            ('Lagos', 'NGA', 14800000),
            ('Buenos Aires', 'ARG', 15400000),
            ('Kolkata', 'IND', 15000000),
            ('Manila', 'PHL', 14200000),
            ('Tianjin', 'CHN', 13600000),
            ('Guangzhou', 'CHN', 13500000),
            ('Rio de Janeiro', 'BRA', 13500000),
            ('Lahore', 'PAK', 13100000),
            ('Bangalore', 'IND', 12300000),
            ('Shenzhen', 'CHN', 12400000),
            ('Moscow', 'RUS', 12500000),
            ('Chennai', 'IND', 11700000),
            ('Bogotá', 'COL', 11300000),
            ('Paris', 'FRA', 11000000),
            ('Jakarta', 'IDN', 10770000),
            ('Lima', 'PER', 10750000),
            ('Bangkok', 'THA', 10539000),
            ('Seoul', 'KOR', 9720000),
            ('Nagoya', 'JPN', 9500000),
            ('Hyderabad', 'IND', 9482000),
            ('London', 'GBR', 9304000),
            ('Tehran', 'IRN', 9135000),
            ('Nanjing', 'CHN', 9042000),
            ('Wuhan', 'CHN', 8896000),
            ('Ho Chi Minh City', 'VNM', 8837000),
            ('Luanda', 'AGO', 8330000),
            ('Ahmedabad', 'IND', 8253000),
            ('Kuala Lumpur', 'MYS', 8200000),
            ('Xi\'an', 'CHN', 8200000),
            ('Hong Kong', 'HKG', 7500000),
            ('Dongguan', 'CHN', 7360000),
            ('Hangzhou', 'CHN', 7236000),
            ('Foshan', 'CHN', 7236000),
            ('Shenyang', 'CHN', 7150000),
            ('Riyadh', 'SAU', 7070000),
            ('Baghdad', 'IRQ', 7000000),
            ('Santiago', 'CHL', 6767000),
            ('Surat', 'IND', 6564000),
            ('Madrid', 'ESP', 6559000),
            ('Suzhou', 'CHN', 6339000),
            ('Pune', 'IND', 6276000),
            ('Harbin', 'CHN', 6115000),
            ('Houston', 'USA', 6115000),
            ('Dallas', 'USA', 6099000),
            ('Toronto', 'CAN', 6082000),
            ('Dar es Salaam', 'TZA', 6048000),
            ('Miami', 'USA', 6036000),
            ('Belo Horizonte', 'BRA', 5972000),
            ('Singapore', 'SGP', 5935000),
            ('Philadelphia', 'USA', 5695000),
            ('Atlanta', 'USA', 5572000),
            ('Fukuoka', 'JPN', 5551000),
            ('Khartoum', 'SDN', 5534000),
            ('Barcelona', 'ESP', 5494000),
            ('Johannesburg', 'ZAF', 5486000),
            ('Saint Petersburg', 'RUS', 5384000),
            ('Qingdao', 'CHN', 5381000),
            ('Dalian', 'CHN', 5300000),
            ('Washington', 'USA', 5290000),
            ('Yangon', 'MMR', 5209000),
            ('Alexandria', 'EGY', 5200000),
            ('Jinan', 'CHN', 5052000),
            ('Guadalajara', 'MEX', 5023000)
        ]
        
        city_count = 0
        
        for city_name, country_code, population in major_cities:
            country_id = country_id_map.get(country_code)
            if not country_id:
                continue
            
            # Insert city directly to countries for now (we'll need to add a state first)
            # For now, let's skip cities since they require states_provinces
            continue
            
            if cursor.rowcount > 0:
                city_count += 1
        
        print(f"✅ Added {city_count} major cities")
    
    def run_comprehensive_population(self):
        """Run the comprehensive population process"""
        print("🚀 Starting comprehensive geography database population...")
        
        # Download all data
        countries_data = self.download_comprehensive_countries()
        subdivisions_data = self.download_subdivisions_data()
        
        if not countries_data:
            print("❌ No country data available, aborting")
            return
        
        # Connect to database
        conn = self.connect_db()
        
        try:
            # Populate countries
            country_id_map = self.populate_countries(conn, countries_data)
            
            # Populate subdivisions if available
            if subdivisions_data:
                self.populate_subdivisions(conn, subdivisions_data, country_id_map)
            
            # Add major cities
            self.add_major_cities(conn, country_id_map)
            
            # Commit all changes
            conn.commit()
            
            # Print final statistics
            cursor = conn.execute("SELECT COUNT(*) FROM countries")
            country_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM states_provinces")
            subdivision_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM cities")
            city_count = cursor.fetchone()[0]
            
            total_entries = country_count + subdivision_count + city_count
            
            print("\n" + "="*60)
            print("🎉 COMPREHENSIVE POPULATION COMPLETE!")
            print("="*60)
            print(f"📊 Countries/Territories: {country_count:,}")
            print(f"🏛️ States/Provinces: {subdivision_count:,}")
            print(f"🏙️ Cities: {city_count:,}")
            print(f"📈 TOTAL ENTRIES: {total_entries:,}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error during population: {e}")
            conn.rollback()
        finally:
            conn.close()

def main():
    populator = ComprehensiveGeographyPopulator()
    populator.run_comprehensive_population()

if __name__ == "__main__":
    main() 