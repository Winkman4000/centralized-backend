#!/usr/bin/env python3
"""
Check population data across years in the temporal geography database.
"""

import sqlite3

def check_temporal_populations():
    """Check population data across years in the temporal database."""
    try:
        # Connect to temporal database
        conn = sqlite3.connect('geography_temporal.db')
        cursor = conn.cursor()
        
        print("🕐 TEMPORAL GEOGRAPHY DATABASE - POPULATION DATA CHECK")
        print("=" * 60)
        
        # Check population data by year
        cursor.execute("""
            SELECT year, 
                   COUNT(*) as total_countries,
                   COUNT(CASE WHEN population IS NOT NULL AND population > 0 THEN 1 END) as with_population,
                   SUM(CASE WHEN population IS NOT NULL THEN population ELSE 0 END) as total_population
            FROM countries_temporal 
            GROUP BY year 
            ORDER BY year
        """)
        
        year_data = cursor.fetchall()
        
        print("\n📊 POPULATION DATA BY YEAR:")
        print("-" * 60)
        for year, total, with_pop, total_pop in year_data:
            coverage = (with_pop / total * 100) if total > 0 else 0
            print(f"{year}: {with_pop}/{total} countries ({coverage:.1f}%) - Total: {total_pop:,}")
        
        # Show top 10 countries for each year with population data
        for year in [2024, 2025]:
            print(f"\n🏆 TOP 10 COUNTRIES BY POPULATION - {year}:")
            print("-" * 60)
            
            cursor.execute("""
                SELECT name, population 
                FROM countries_temporal 
                WHERE year = ? AND population IS NOT NULL AND population > 0
                ORDER BY population DESC 
                LIMIT 10
            """, (year,))
            
            top_countries = cursor.fetchall()
            if top_countries:
                for i, (name, pop) in enumerate(top_countries, 1):
                    print(f"   {i:2d}. {name}: {pop:,}")
            else:
                print(f"   No population data available for {year}")
        
        # Compare 2024 vs 2025 for top countries
        print(f"\n📈 POPULATION COMPARISON: 2024 vs 2025")
        print("-" * 60)
        
        cursor.execute("""
            SELECT c2024.name, c2024.population as pop_2024, c2025.population as pop_2025,
                   (c2025.population - c2024.population) as change,
                   ROUND((c2025.population - c2024.population) * 100.0 / c2024.population, 2) as change_percent
            FROM countries_temporal c2024
            JOIN countries_temporal c2025 ON c2024.name = c2025.name
            WHERE c2024.year = 2024 AND c2025.year = 2025
            AND c2024.population IS NOT NULL AND c2025.population IS NOT NULL
            AND c2024.population > 0 AND c2025.population > 0
            ORDER BY c2024.population DESC
            LIMIT 10
        """)
        
        comparisons = cursor.fetchall()
        if comparisons:
            print("Country | 2024 Population | 2025 Population | Change | Change %")
            print("-" * 60)
            for name, pop_2024, pop_2025, change, change_pct in comparisons:
                change_str = f"+{change:,}" if change >= 0 else f"{change:,}"
                change_pct_str = f"+{change_pct}%" if change_pct >= 0 else f"{change_pct}%"
                print(f"{name[:20]:20} | {pop_2024:13,} | {pop_2025:13,} | {change_str:7} | {change_pct_str:7}")
        else:
            print("No comparison data available")
        
        # Check for countries missing population data in either year
        print(f"\n❓ COUNTRIES MISSING POPULATION DATA:")
        print("-" * 60)
        
        for year in [2024, 2025]:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM countries_temporal 
                WHERE year = ? AND (population IS NULL OR population = 0)
            """, (year,))
            
            missing_count = cursor.fetchone()[0]
            print(f"{year}: {missing_count} countries missing population data")
            
            if missing_count > 0 and missing_count <= 20:  # Show if reasonable number
                cursor.execute("""
                    SELECT name 
                    FROM countries_temporal 
                    WHERE year = ? AND (population IS NULL OR population = 0)
                    ORDER BY name
                """, (year,))
                
                missing_countries = cursor.fetchall()
                print(f"   Missing in {year}: {', '.join([c[0] for c in missing_countries])}")
        
        conn.close()
        print(f"\n✅ Temporal population data check completed!")
        
    except Exception as e:
        print(f"❌ Error checking temporal populations: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_temporal_populations() 