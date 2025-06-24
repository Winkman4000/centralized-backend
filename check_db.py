#!/usr/bin/env python3
import sqlite3

db = sqlite3.connect('geography.db')
db.row_factory = sqlite3.Row

print("=== CONTINENTS ===")
cursor = db.execute('SELECT * FROM continents ORDER BY name')
for row in cursor.fetchall():
    print(f"{row['name']} ({row['code']})")

print("\n=== COUNTRIES BY CONTINENT ===")
cursor = db.execute('''
    SELECT cont.name as continent, COUNT(c.id) as count
    FROM continents cont
    LEFT JOIN countries c ON cont.id = c.continent_id
    GROUP BY cont.id, cont.name
    ORDER BY count DESC
''')
for row in cursor.fetchall():
    print(f"{row['continent']}: {row['count']} countries")

print("\n=== ANTARCTICA COUNTRIES ===")
cursor = db.execute('''
    SELECT c.name, c.code_iso2 
    FROM countries c 
    JOIN continents cont ON c.continent_id = cont.id 
    WHERE cont.name = 'Antarctica'
''')
for row in cursor.fetchall():
    print(f"{row['name']} ({row['code_iso2']})")

print(f"\n=== TOTAL COUNTRIES ===")
cursor = db.execute('SELECT COUNT(*) as total FROM countries')
total = cursor.fetchone()['total']
print(f"Total: {total}")

db.close() 