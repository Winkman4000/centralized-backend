#!/usr/bin/env python3
"""
Ultimate Geographical Database Manager
Hierarchical structure: Continents > Countries > States/Provinces > Cities/Towns
"""

import sqlite3
import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json

app = Flask(__name__)
app.config['DATABASE'] = 'geography.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return db

def init_database():
    """Initialize the database with schema and sample data"""
    if os.path.exists(app.config['DATABASE']):
        print("Database already exists. Skipping initialization.")
        return
    
    print("Creating new database...")
    with open('database_schema.sql', 'r') as f:
        schema = f.read()
    
    db = get_db()
    db.executescript(schema)
    db.commit()
    db.close()
    print("Database initialized successfully!")

# API ENDPOINTS

@app.route('/api/continents', methods=['GET'])
def get_continents():
    """Get all continents"""
    db = get_db()
    cursor = db.execute('SELECT * FROM continents ORDER BY name')
    continents = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'continents': continents,
        'count': len(continents)
    })

@app.route('/api/countries', methods=['GET'])
def get_all_countries():
    """Get all countries with continent info and religious distribution"""
    db = get_db()
    cursor = db.execute('''
        SELECT c.*, cont.name as continent_name 
        FROM countries c 
        JOIN continents cont ON c.continent_id = cont.id 
        ORDER BY cont.name, c.name
    ''')
    
    countries = []
    for row in cursor.fetchall():
        country = dict(row)
        # Group religious data into a nested object for cleaner API response
        if 'religion_christian_percent' in country:
            country['religious_distribution'] = {
                'christian_percent': country.get('religion_christian_percent', 0),
                'muslim_percent': country.get('religion_muslim_percent', 0),
                'hindu_percent': country.get('religion_hindu_percent', 0),
                'buddhist_percent': country.get('religion_buddhist_percent', 0),
                'jewish_percent': country.get('religion_jewish_percent', 0),
                'other_percent': country.get('religion_other_percent', 0),
                'nonreligious_percent': country.get('religion_nonreligious_percent', 0)
            }
            # Remove individual religion fields to clean up response
            for key in list(country.keys()):
                if key.startswith('religion_'):
                    del country[key]
        
        countries.append(country)
    
    db.close()
    
    return jsonify({
        'countries': countries,
        'count': len(countries)
    })

@app.route('/api/continents/<int:continent_id>/countries', methods=['GET'])
def get_countries_by_continent(continent_id):
    """Get all countries in a continent"""
    db = get_db()
    cursor = db.execute('''
        SELECT c.*, cont.name as continent_name 
        FROM countries c 
        JOIN continents cont ON c.continent_id = cont.id 
        WHERE c.continent_id = ? 
        ORDER BY c.name
    ''', (continent_id,))
    
    countries = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'countries': countries,
        'count': len(countries)
    })

@app.route('/api/hierarchy', methods=['GET'])
def get_full_hierarchy():
    """Get the complete location hierarchy"""
    db = get_db()
    cursor = db.execute('SELECT * FROM location_hierarchy ORDER BY full_path')
    hierarchy = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'hierarchy': hierarchy,
        'count': len(hierarchy)
    })

@app.route('/api/search', methods=['GET'])
def search_locations():
    """Search for locations by name"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    search_term = f'%{query}%'
    db = get_db()
    
    results = {
        'continents': [],
        'countries': [],
        'states_provinces': [],
        'cities': []
    }
    
    # Search continents
    cursor = db.execute('SELECT * FROM continents WHERE name LIKE ? ORDER BY name', (search_term,))
    results['continents'] = [dict(row) for row in cursor.fetchall()]
    
    # Search cities
    cursor = db.execute('''
        SELECT * FROM location_hierarchy 
        WHERE city_name LIKE ?
        ORDER BY city_population DESC
    ''', (search_term,))
    results['cities'] = [dict(row) for row in cursor.fetchall()]
    
    db.close()
    total_results = sum(len(results[key]) for key in results)
    
    return jsonify({
        'query': query,
        'results': results,
        'total_results': total_results
    })

# ADD/EDIT ENDPOINTS

@app.route('/api/continents', methods=['POST'])
def add_continent():
    """Add a new continent"""
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    db = get_db()
    try:
        cursor = db.execute('''
            INSERT INTO continents (name, code, area_km2, population)
            VALUES (?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('code'),
            data.get('area_km2'),
            data.get('population')
        ))
        
        continent_id = cursor.lastrowid
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'continent_id': continent_id,
            'message': f'Continent "{data["name"]}" added successfully'
        })
    
    except sqlite3.IntegrityError as e:
        db.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 400

# WEB INTERFACE

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌍 Ultimate Geography Database</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .nav { margin: 20px 0; text-align: center; }
        .nav button { margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .nav button:hover { background: #0056b3; }
        .nav button.active { background: #28a745; }
        .tab { display: none; }
        .tab.active { display: block; }
        .hierarchy { max-height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 20px; }
        .location { margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #218838; }
        .search-box { width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Ultimate Geography Database</h1>
        <p style="text-align: center; color: #666;">Hierarchical structure: Continents → Countries → States/Provinces → Cities/Towns</p>
        
        <div class="nav">
            <button onclick="showTab('countries')" class="active" id="countries-btn">All Countries</button>
            <button onclick="showTab('browse')" id="browse-btn">Browse Hierarchy</button>
            <button onclick="showTab('search')" id="search-btn">Search</button>
            <button onclick="showTab('add')" id="add-btn">Add Locations</button>
        </div>
        
        <div id="countries" class="tab active">
            <h3>All Countries by Continent</h3>
            <div id="countries-container" class="hierarchy">
                <div>Loading countries...</div>
            </div>
        </div>
        
        <div id="browse" class="tab">
            <h3>Browse Location Hierarchy</h3>
            <div id="hierarchy-container" class="hierarchy">
                <div>Loading hierarchy...</div>
            </div>
        </div>
        
        <div id="search" class="tab">
            <h3>Search Locations</h3>
            <input type="text" class="search-box" id="searchInput" placeholder="Search for continents, countries, states, or cities..." onkeyup="performSearch()">
            <div id="search-results"></div>
        </div>
        
        <div id="add" class="tab">
            <h3>Add New Locations</h3>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h4>Add Continent</h4>
                <div class="form-group">
                    <label>Name:</label>
                    <input type="text" id="continent-name" placeholder="e.g., Antarctica">
                </div>
                <div class="form-group">
                    <label>Code:</label>
                    <input type="text" id="continent-code" placeholder="e.g., AN">
                </div>
                <button class="btn" onclick="addContinent()">Add Continent</button>
            </div>
            
            <div id="add-messages"></div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.getElementById(tabName + '-btn').classList.add('active');
            
            if (tabName === 'browse') {
                loadHierarchy();
            } else if (tabName === 'countries') {
                loadCountries();
            }
        }
        
        function loadHierarchy() {
            fetch('/api/hierarchy')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('hierarchy-container');
                    container.innerHTML = '';
                    
                    data.hierarchy.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'location';
                        div.innerHTML = `
                            <strong>${item.full_path}</strong><br>
                            <small>Population: ${item.city_population ? item.city_population.toLocaleString() : 'N/A'} | Type: ${item.city_type}</small>
                        `;
                        container.appendChild(div);
                    });
                })
                .catch(error => {
                    document.getElementById('hierarchy-container').innerHTML = '<div class="error">Error loading hierarchy</div>';
                });
        }
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (query.length < 2) {
                document.getElementById('search-results').innerHTML = '';
                return;
            }
            
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('search-results');
                    container.innerHTML = '';
                    
                    if (data.total_results === 0) {
                        container.innerHTML = '<div>No results found</div>';
                        return;
                    }
                    
                    ['continents', 'cities'].forEach(category => {
                        if (data.results[category].length > 0) {
                            const section = document.createElement('div');
                            section.innerHTML = `<h4>${category.toUpperCase()}</h4>`;
                            
                            data.results[category].forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'location';
                                
                                if (category === 'cities') {
                                    div.innerHTML = `
                                        <strong>${item.full_path}</strong><br>
                                        <small>Population: ${item.city_population ? item.city_population.toLocaleString() : 'N/A'}</small>
                                    `;
                                } else {
                                    div.innerHTML = `
                                        <strong>${item.name}</strong><br>
                                        <small>Code: ${item.code || 'N/A'}</small>
                                    `;
                                }
                                section.appendChild(div);
                            });
                            container.appendChild(section);
                        }
                    });
                });
        }
        
        function addContinent() {
            const name = document.getElementById('continent-name').value.trim();
            const code = document.getElementById('continent-code').value.trim();
            
            if (!name) {
                showMessage('error', 'Continent name is required');
                return;
            }
            
            fetch('/api/continents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    code: code || null
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('success', data.message);
                    document.getElementById('continent-name').value = '';
                    document.getElementById('continent-code').value = '';
                } else {
                    showMessage('error', data.error);
                }
            })
            .catch(error => {
                showMessage('error', 'Error adding continent');
            });
        }
        
        function showMessage(type, message) {
            const container = document.getElementById('add-messages');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = message;
            container.appendChild(div);
            
            setTimeout(() => div.remove(), 5000);
        }
        
        function loadCountries() {
            fetch('/api/countries')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('countries-container');
                    container.innerHTML = '';
                    
                    // Group countries by continent
                    const continents = {};
                    data.countries.forEach(country => {
                        if (!continents[country.continent_name]) {
                            continents[country.continent_name] = [];
                        }
                        continents[country.continent_name].push(country);
                    });
                    
                    // Display by continent
                    Object.keys(continents).sort().forEach(continentName => {
                        const section = document.createElement('div');
                        section.innerHTML = `<h4>${continentName} (${continents[continentName].length} countries)</h4>`;
                        
                        continents[continentName].forEach(country => {
                            const div = document.createElement('div');
                            div.className = 'location';
                            
                            // Build religious distribution display
                            let religionText = '';
                            if (country.religious_distribution) {
                                const religions = [];
                                const rd = country.religious_distribution;
                                if (rd.christian_percent > 0) religions.push(`Christian: ${rd.christian_percent}%`);
                                if (rd.muslim_percent > 0) religions.push(`Muslim: ${rd.muslim_percent}%`);
                                if (rd.hindu_percent > 0) religions.push(`Hindu: ${rd.hindu_percent}%`);
                                if (rd.buddhist_percent > 0) religions.push(`Buddhist: ${rd.buddhist_percent}%`);
                                if (rd.jewish_percent > 0) religions.push(`Jewish: ${rd.jewish_percent}%`);
                                if (rd.other_percent > 0) religions.push(`Other: ${rd.other_percent}%`);
                                if (rd.nonreligious_percent > 0) religions.push(`Non-religious: ${rd.nonreligious_percent}%`);
                                religionText = religions.length > 0 ? `<br><small style="color: #666;">🕊️ ${religions.join(', ')}</small>` : '';
                            }
                            
                            div.innerHTML = `
                                <strong>${country.name}</strong> (${country.code_iso2})<br>
                                <small>Capital: ${country.capital || 'N/A'} | Population: ${country.population ? country.population.toLocaleString() : 'N/A'} | Currency: ${country.currency || 'N/A'}</small>
                                ${religionText}
                            `;
                            section.appendChild(div);
                        });
                        container.appendChild(section);
                    });
                })
                .catch(error => {
                    document.getElementById('countries-container').innerHTML = '<div class="error">Error loading countries</div>';
                });
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadCountries();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'connected'})

if __name__ == '__main__':
    print("🌍 Starting Ultimate Geography Database...")
    init_database()
    
    print("\n" + "="*60)
    print("🚀 Geography Database Server Ready!")
    print("📊 Web Interface: http://localhost:5000")
    print("🔍 API Documentation: http://localhost:5000/api/continents")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 