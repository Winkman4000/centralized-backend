#!/usr/bin/env python3
"""
Temporal Geographical Database Manager
3D Database with time dimension: Years > Continents > Countries
"""

import sqlite3
import os
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json

app = Flask(__name__)
app.config['DATABASE'] = 'geography_temporal.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return db

# API ENDPOINTS

@app.route('/api/years', methods=['GET'])
def get_available_years():
    """Get all available years in the database"""
    db = get_db()
    cursor = db.execute('SELECT DISTINCT year FROM continents_temporal ORDER BY year DESC')
    years = [row[0] for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'years': years,
        'count': len(years),
        'latest': years[0] if years else None
    })

@app.route('/api/continents', methods=['GET'])
def get_continents():
    """Get all continents for a specific year"""
    year = request.args.get('year', 2025, type=int)
    
    db = get_db()
    cursor = db.execute('''
        SELECT continent_id, name, code 
        FROM continents_temporal 
        WHERE year = ? 
        ORDER BY name
    ''', (year,))
    continents = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'continents': continents,
        'count': len(continents),
        'year': year
    })

@app.route('/api/countries', methods=['GET'])
def get_all_countries():
    """Get all countries with continent info for a specific year"""
    year = request.args.get('year', 2025, type=int)
    
    db = get_db()
    cursor = db.execute('''
        SELECT c.*, cont.name as continent_name 
        FROM countries_temporal c 
        JOIN continents_temporal cont ON c.continent_id = cont.continent_id AND c.year = cont.year
        WHERE c.year = ?
        ORDER BY cont.name, c.name
    ''', (year,))
    
    countries = []
    for row in cursor.fetchall():
        country = dict(row)
        # Group religious data into a nested object for cleaner API response
        if 'religion_christian_percent' in country:
            country['religious_distribution'] = {
                'christian_percent': country.get('religion_christian_percent', 0) or 0,
                'muslim_percent': country.get('religion_muslim_percent', 0) or 0,
                'hindu_percent': country.get('religion_hindu_percent', 0) or 0,
                'buddhist_percent': country.get('religion_buddhist_percent', 0) or 0,
                'jewish_percent': country.get('religion_jewish_percent', 0) or 0,
                'other_percent': country.get('religion_other_percent', 0) or 0,
                'nonreligious_percent': country.get('religion_nonreligious_percent', 0) or 0
            }
            # Remove individual religion fields to clean up response
            for key in list(country.keys()):
                if key.startswith('religion_'):
                    del country[key]
        
        # Group race/ethnicity data into a nested object for cleaner API response
        if 'race_white_percent' in country:
            country['racial_ethnic_distribution'] = {
                'white_percent': country.get('race_white_percent', 0) or 0,
                'black_percent': country.get('race_black_percent', 0) or 0,
                'asian_percent': country.get('race_asian_percent', 0) or 0,
                'hispanic_percent': country.get('race_hispanic_percent', 0) or 0,
                'native_american_percent': country.get('race_native_american_percent', 0) or 0,
                'pacific_islander_percent': country.get('race_pacific_islander_percent', 0) or 0,
                'other_percent': country.get('race_other_percent', 0) or 0
            }
            # Remove individual race fields to clean up response
            for key in list(country.keys()):
                if key.startswith('race_'):
                    del country[key]
        
        # Handle territories data
        if 'territories' in country and country['territories']:
            territories_list = [t.strip() for t in country['territories'].split(',')]
            country['administrative_divisions'] = {
                'territories': territories_list,
                'count': len(territories_list)
            }
            # Keep territories field for backward compatibility but also provide structured data
        elif 'territories' in country:
            country['administrative_divisions'] = {
                'territories': [],
                'count': 0
            }
        
        countries.append(country)
    
    db.close()
    
    return jsonify({
        'countries': countries,
        'count': len(countries),
        'year': year
    })

@app.route('/api/continents/<int:continent_id>/countries', methods=['GET'])
def get_countries_by_continent(continent_id):
    """Get all countries in a continent for a specific year"""
    year = request.args.get('year', 2025, type=int)
    
    db = get_db()
    cursor = db.execute('''
        SELECT c.*, cont.name as continent_name 
        FROM countries_temporal c 
        JOIN continents_temporal cont ON c.continent_id = cont.continent_id AND c.year = cont.year
        WHERE c.continent_id = ? AND c.year = ?
        ORDER BY c.name
    ''', (continent_id, year))
    
    countries = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'countries': countries,
        'count': len(countries),
        'continent_id': continent_id,
        'year': year
    })

@app.route('/api/country/<name>/timeline', methods=['GET'])
def get_country_timeline(name):
    """Get a country's data across all years"""
    db = get_db()
    cursor = db.execute('''
        SELECT year, population, capital, territories,
               religion_christian_percent, religion_muslim_percent, religion_hindu_percent,
               religion_buddhist_percent, religion_jewish_percent, religion_other_percent,
               religion_nonreligious_percent,
               race_white_percent, race_black_percent, race_asian_percent,
               race_hispanic_percent, race_native_american_percent, race_pacific_islander_percent,
               race_other_percent
        FROM countries_temporal 
        WHERE name = ? 
        ORDER BY year
    ''', (name,))
    
    timeline = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify({
        'country': name,
        'timeline': timeline,
        'years': len(timeline)
    })

@app.route('/api/search', methods=['GET'])
def search_locations():
    """Search for locations by name in a specific year"""
    query = request.args.get('q', '').strip()
    year = request.args.get('year', 2025, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    search_term = f'%{query}%'
    db = get_db()
    
    results = {
        'continents': [],
        'countries': []
    }
    
    # Search continents
    cursor = db.execute('''
        SELECT continent_id, name, code 
        FROM continents_temporal 
        WHERE name LIKE ? AND year = ? 
        ORDER BY name
    ''', (search_term, year))
    results['continents'] = [dict(row) for row in cursor.fetchall()]
    
    # Search countries
    cursor = db.execute('''
        SELECT c.*, cont.name as continent_name
        FROM countries_temporal c
        JOIN continents_temporal cont ON c.continent_id = cont.continent_id AND c.year = cont.year
        WHERE c.name LIKE ? AND c.year = ?
        ORDER BY c.name
    ''', (search_term, year))
    results['countries'] = [dict(row) for row in cursor.fetchall()]
    
    db.close()
    total_results = sum(len(results[key]) for key in results)
    
    return jsonify({
        'query': query,
        'year': year,
        'results': results,
        'total_results': total_results
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics for a specific year"""
    year = request.args.get('year', 2025, type=int)
    
    db = get_db()
    
    # Get continent counts
    cursor = db.execute('''
        SELECT cont.name, COUNT(c.country_id) as country_count,
               SUM(CASE WHEN c.population IS NOT NULL THEN 1 ELSE 0 END) as countries_with_population
        FROM continents_temporal cont
        LEFT JOIN countries_temporal c ON cont.continent_id = c.continent_id AND cont.year = c.year
        WHERE cont.year = ?
        GROUP BY cont.continent_id, cont.name
        ORDER BY country_count DESC
    ''', (year,))
    
    continent_stats = [dict(row) for row in cursor.fetchall()]
    
    # Get overall stats
    cursor = db.execute('''
        SELECT 
            COUNT(*) as total_countries,
            SUM(CASE WHEN population IS NOT NULL THEN 1 ELSE 0 END) as countries_with_population,
            SUM(CASE WHEN population IS NOT NULL THEN population ELSE 0 END) as total_population
        FROM countries_temporal 
        WHERE year = ?
    ''', (year,))
    
    overall_stats = dict(cursor.fetchone())
    db.close()
    
    return jsonify({
        'year': year,
        'overall': overall_stats,
        'by_continent': continent_stats
    })

# WEB INTERFACE HTML TEMPLATE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Temporal Geography Database</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border-radius: 10px;
        }
        .year-selector {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        .year-selector h3 {
            margin-bottom: 15px;
            color: #495057;
        }
        .year-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .year-btn {
            padding: 10px 20px;
            border: 2px solid #007bff;
            background: white;
            color: #007bff;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }
        .year-btn:hover {
            background: #007bff;
            color: white;
            transform: translateY(-2px);
        }
        .year-btn.active {
            background: #007bff;
            color: white;
            box-shadow: 0 4px 8px rgba(0,123,255,0.3);
        }
        .tabs {
            display: flex;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 20px;
        }
        .tab-button {
            flex: 1;
            padding: 15px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .tab-button.active {
            background: #007bff;
            color: white;
        }
        .tab-content {
            display: none;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .tab-content.active {
            display: block;
        }
        .location {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .search-box {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
        }
        .search-box:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 10px rgba(0,123,255,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .current-year {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            z-index: 1000;
        }
        .error { color: #dc3545; padding: 20px; text-align: center; }
        .loading { text-align: center; padding: 40px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="current-year" id="current-year">Year: 2025</div>
    
    <div class="container">
        <div class="header">
            <h1>🌍 Temporal Geography Database</h1>
            <p>Explore countries and continents across time (2020-2025)</p>
        </div>
        
        <div class="year-selector">
            <h3>🕐 Select Year to View</h3>
            <div class="year-buttons" id="year-buttons">
                <!-- Year buttons will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('countries')">All Countries</button>
            <button class="tab-button" onclick="showTab('search')">Search</button>
            <button class="tab-button" onclick="showTab('stats')">Statistics</button>
            <button class="tab-button" onclick="showTab('timeline')">Country Timeline</button>
        </div>
        
        <div id="countries" class="tab-content active">
            <div id="countries-container" class="loading">Loading countries...</div>
        </div>
        
        <div id="search" class="tab-content">
            <input type="text" id="searchInput" class="search-box" placeholder="Search for countries or continents..." oninput="performSearch()">
            <div id="search-results"></div>
        </div>
        
        <div id="stats" class="tab-content">
            <div id="stats-container" class="loading">Loading statistics...</div>
        </div>
        
        <div id="timeline" class="tab-content">
            <input type="text" id="timelineInput" class="search-box" placeholder="Enter country name to see timeline (e.g., United States, China, India)..." oninput="loadTimeline()">
            <div id="timeline-container"></div>
        </div>
    </div>

    <script>
        let currentYear = 2025;
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            loadAvailableYears();
        });
        
        function loadAvailableYears() {
            fetch('/api/years')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('year-buttons');
                    container.innerHTML = '';
                    
                    data.years.forEach(year => {
                        const btn = document.createElement('button');
                        btn.className = `year-btn ${year === currentYear ? 'active' : ''}`;
                        btn.textContent = year;
                        btn.onclick = () => selectYear(year);
                        container.appendChild(btn);
                    });
                    
                    // Load initial data
                    loadCountries();
                    loadStats();
                })
                .catch(error => {
                    console.error('Error loading years:', error);
                });
        }
        
        function selectYear(year) {
            currentYear = year;
            document.getElementById('current-year').textContent = `Year: ${year}`;
            
            // Update active year button
            document.querySelectorAll('.year-btn').forEach(btn => {
                btn.classList.toggle('active', btn.textContent == year);
            });
            
            // Reload current tab data
            const activeTab = document.querySelector('.tab-button.active').onclick.toString().match(/showTab\\('(.+?)'\\)/)[1];
            if (activeTab === 'countries') loadCountries();
            else if (activeTab === 'stats') loadStats();
            else if (activeTab === 'search') performSearch();
        }
        
        function showTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            
            // Load data for the tab
            if (tabName === 'countries') {
                loadCountries();
            } else if (tabName === 'stats') {
                loadStats();
            }
        }
        
        function loadCountries() {
            document.getElementById('countries-container').innerHTML = '<div class="loading">Loading countries...</div>';
            
            fetch(`/api/countries?year=${currentYear}`)
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
                            
                            // Build race/ethnicity distribution display
                            let raceText = '';
                            if (country.racial_ethnic_distribution) {
                                const races = [];
                                const red = country.racial_ethnic_distribution;
                                if (red.white_percent > 0) races.push(`White: ${red.white_percent}%`);
                                if (red.black_percent > 0) races.push(`Black: ${red.black_percent}%`);
                                if (red.asian_percent > 0) races.push(`Asian: ${red.asian_percent}%`);
                                if (red.hispanic_percent > 0) races.push(`Hispanic: ${red.hispanic_percent}%`);
                                if (red.native_american_percent > 0) races.push(`Native: ${red.native_american_percent}%`);
                                if (red.pacific_islander_percent > 0) races.push(`Pacific: ${red.pacific_islander_percent}%`);
                                if (red.other_percent > 0) races.push(`Other: ${red.other_percent}%`);
                                raceText = races.length > 0 ? `<br><small style="color: #666;">🌍 ${races.join(', ')}</small>` : '';
                            }
                            
                            // Build territories/administrative divisions display
                            let territoriesText = '';
                            if (country.administrative_divisions && country.administrative_divisions.count > 0) {
                                const count = country.administrative_divisions.count;
                                const firstFew = country.administrative_divisions.territories.slice(0, 3).join(', ');
                                const remaining = count > 3 ? ` (+${count - 3} more)` : '';
                                territoriesText = `<br><small style="color: #666;">🏛️ Territories (${count}): ${firstFew}${remaining}</small>`;
                            }
                            
                            const populationText = country.population ? country.population.toLocaleString() : 'No data';
                            const capitalText = country.capital ? `<br><small>🏛️ Capital: ${country.capital}</small>` : '';
                            
                            div.innerHTML = `
                                <strong>${country.name}</strong> (${country.code_iso2 || 'N/A'})<br>
                                <small>Population: ${populationText}</small>
                                ${capitalText}
                                ${religionText}
                                ${raceText}
                                ${territoriesText}
                                <br><small style="color: #007bff; cursor: pointer;" onclick="loadCountryTimeline('${country.name}')">📊 View Timeline</small>
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
        
        function loadStats() {
            document.getElementById('stats-container').innerHTML = '<div class="loading">Loading statistics...</div>';
            
            fetch(`/api/stats?year=${currentYear}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('stats-container');
                    container.innerHTML = '';
                    
                    // Overall stats
                    const overallDiv = document.createElement('div');
                    overallDiv.innerHTML = `<h3>📊 Overall Statistics for ${data.year}</h3>`;
                    
                    const statsGrid = document.createElement('div');
                    statsGrid.className = 'stats-grid';
                    
                    const totalCountriesCard = document.createElement('div');
                    totalCountriesCard.className = 'stat-card';
                    totalCountriesCard.innerHTML = `
                        <div class="stat-number">${data.overall.total_countries}</div>
                        <div>Total Countries</div>
                    `;
                    
                    const withPopulationCard = document.createElement('div');
                    withPopulationCard.className = 'stat-card';
                    withPopulationCard.innerHTML = `
                        <div class="stat-number">${data.overall.countries_with_population}</div>
                        <div>Countries with Population Data</div>
                    `;
                    
                    const totalPopulationCard = document.createElement('div');
                    totalPopulationCard.className = 'stat-card';
                    totalPopulationCard.innerHTML = `
                        <div class="stat-number">${data.overall.total_population.toLocaleString()}</div>
                        <div>Total Population</div>
                    `;
                    
                    statsGrid.appendChild(totalCountriesCard);
                    statsGrid.appendChild(withPopulationCard);
                    statsGrid.appendChild(totalPopulationCard);
                    
                    container.appendChild(overallDiv);
                    container.appendChild(statsGrid);
                    
                    // By continent stats
                    const continentDiv = document.createElement('div');
                    continentDiv.innerHTML = `<h3>🌍 By Continent</h3>`;
                    
                    data.by_continent.forEach(continent => {
                        const div = document.createElement('div');
                        div.className = 'location';
                        div.innerHTML = `
                            <strong>${continent.name}</strong><br>
                            <small>Countries: ${continent.country_count} | With Population Data: ${continent.countries_with_population}</small>
                        `;
                        continentDiv.appendChild(div);
                    });
                    
                    container.appendChild(continentDiv);
                })
                .catch(error => {
                    document.getElementById('stats-container').innerHTML = '<div class="error">Error loading statistics</div>';
                });
        }
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (query.length < 2) {
                document.getElementById('search-results').innerHTML = '';
                return;
            }
            
            fetch(`/api/search?q=${encodeURIComponent(query)}&year=${currentYear}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('search-results');
                    container.innerHTML = '';
                    
                    if (data.total_results === 0) {
                        container.innerHTML = `<div>No results found for "${query}" in ${data.year}</div>`;
                        return;
                    }
                    
                    ['continents', 'countries'].forEach(category => {
                        if (data.results[category].length > 0) {
                            const section = document.createElement('div');
                            section.innerHTML = `<h4>${category.toUpperCase()} (${data.results[category].length})</h4>`;
                            
                            data.results[category].forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'location';
                                
                                if (category === 'countries') {
                                    const populationText = item.population ? item.population.toLocaleString() : 'No data';
                                    const capitalText = item.capital ? ` | Capital: ${item.capital}` : '';
                                    div.innerHTML = `
                                        <strong>${item.name}</strong> (${item.code_iso2 || 'N/A'})<br>
                                        <small>Continent: ${item.continent_name} | Population: ${populationText}${capitalText}</small>
                                        <br><small style="color: #007bff; cursor: pointer;" onclick="loadCountryTimeline('${item.name}')">📊 View Timeline</small>
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
        
        function loadTimeline() {
            const country = document.getElementById('timelineInput').value.trim();
            if (country.length < 2) {
                document.getElementById('timeline-container').innerHTML = '';
                return;
            }
            
            loadCountryTimeline(country);
        }
        
        function loadCountryTimeline(countryName) {
            // Switch to timeline tab
            showTab('timeline');
            document.getElementById('timelineInput').value = countryName;
            
            fetch(`/api/country/${encodeURIComponent(countryName)}/timeline`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('timeline-container');
                    container.innerHTML = '';
                    
                    if (data.timeline.length === 0) {
                        container.innerHTML = `<div>No data found for "${countryName}"</div>`;
                        return;
                    }
                    
                    const header = document.createElement('div');
                    header.innerHTML = `<h3>📈 ${data.country} Timeline (${data.years} years)</h3>`;
                    container.appendChild(header);
                    
                    data.timeline.forEach(yearData => {
                        const div = document.createElement('div');
                        div.className = 'location';
                        
                        const populationText = yearData.population ? yearData.population.toLocaleString() : 'No data';
                        const capitalText = yearData.capital ? `<br><small>🏛️ Capital: ${yearData.capital}</small>` : '';
                        
                        // Build religious data if available
                        let religionText = '';
                        if (yearData.religion_christian_percent !== null) {
                            const religions = [];
                            if (yearData.religion_christian_percent > 0) religions.push(`Christian: ${yearData.religion_christian_percent}%`);
                            if (yearData.religion_muslim_percent > 0) religions.push(`Muslim: ${yearData.religion_muslim_percent}%`);
                            if (yearData.religion_hindu_percent > 0) religions.push(`Hindu: ${yearData.religion_hindu_percent}%`);
                            if (yearData.religion_buddhist_percent > 0) religions.push(`Buddhist: ${yearData.religion_buddhist_percent}%`);
                            if (yearData.religion_jewish_percent > 0) religions.push(`Jewish: ${yearData.religion_jewish_percent}%`);
                            if (yearData.religion_other_percent > 0) religions.push(`Other: ${yearData.religion_other_percent}%`);
                            if (yearData.religion_nonreligious_percent > 0) religions.push(`Non-religious: ${yearData.religion_nonreligious_percent}%`);
                            religionText = religions.length > 0 ? `<br><small style="color: #666;">🕊️ ${religions.join(', ')}</small>` : '';
                        }
                        
                        // Build race/ethnicity data if available
                        let raceText = '';
                        if (yearData.race_white_percent !== null) {
                            const races = [];
                            if (yearData.race_white_percent > 0) races.push(`White: ${yearData.race_white_percent}%`);
                            if (yearData.race_black_percent > 0) races.push(`Black: ${yearData.race_black_percent}%`);
                            if (yearData.race_asian_percent > 0) races.push(`Asian: ${yearData.race_asian_percent}%`);
                            if (yearData.race_hispanic_percent > 0) races.push(`Hispanic: ${yearData.race_hispanic_percent}%`);
                            if (yearData.race_native_american_percent > 0) races.push(`Native: ${yearData.race_native_american_percent}%`);
                            if (yearData.race_pacific_islander_percent > 0) races.push(`Pacific: ${yearData.race_pacific_islander_percent}%`);
                            if (yearData.race_other_percent > 0) races.push(`Other: ${yearData.race_other_percent}%`);
                            raceText = races.length > 0 ? `<br><small style="color: #666;">🌍 ${races.join(', ')}</small>` : '';
                        }
                        
                        div.innerHTML = `
                            <strong>${yearData.year}</strong><br>
                            <small>Population: ${populationText}</small>
                            ${capitalText}
                            ${religionText}
                            ${raceText}
                        `;
                        container.appendChild(div);
                    });
                })
                .catch(error => {
                    document.getElementById('timeline-container').innerHTML = `<div class="error">Error loading timeline for "${countryName}"</div>`;
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'temporal', 'type': '3D with time dimension'})

if __name__ == '__main__':
    print("🕐 Starting Temporal Geography Database...")
    
    if not os.path.exists(app.config['DATABASE']):
        print("❌ Temporal database not found! Please run create_temporal_database.py first.")
        exit(1)
    
    print("\n" + "="*60)
    print("🚀 Temporal Geography Database Server Ready!")
    print("📊 Web Interface: http://localhost:5001")
    print("🕐 Features: Year selector, timeline view, temporal queries")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 