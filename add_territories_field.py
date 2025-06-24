#!/usr/bin/env python3

import sqlite3

def add_territories_field():
    """Add territories/administrative divisions field to countries"""
    
    conn = sqlite3.connect('geography_temporal.db')
    cursor = conn.cursor()
    
    # First, check current schema
    cursor.execute('PRAGMA table_info(countries_temporal)')
    columns = cursor.fetchall()
    print("Current database columns:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Check if territories field already exists
    column_names = [col[1] for col in columns]
    if 'territories' not in column_names:
        print("\n🏗️ Adding territories field...")
        cursor.execute('ALTER TABLE countries_temporal ADD COLUMN territories TEXT')
        print("✅ Territories field added successfully!")
    else:
        print("\nℹ️ Territories field already exists")
    
    # Sample territories data for major countries
    territories_data = {
        'United States': 'Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming',
        
        'Canada': 'Alberta, British Columbia, Manitoba, New Brunswick, Newfoundland and Labrador, Northwest Territories, Nova Scotia, Nunavut, Ontario, Prince Edward Island, Quebec, Saskatchewan, Yukon',
        
        'Australia': 'Australian Capital Territory, New South Wales, Northern Territory, Queensland, South Australia, Tasmania, Victoria, Western Australia',
        
        'Germany': 'Baden-Württemberg, Bavaria, Berlin, Brandenburg, Bremen, Hamburg, Hesse, Lower Saxony, Mecklenburg-Vorpommern, North Rhine-Westphalia, Rhineland-Palatinate, Saarland, Saxony, Saxony-Anhalt, Schleswig-Holstein, Thuringia',
        
        'United Kingdom': 'England, Scotland, Wales, Northern Ireland',
        
        'France': 'Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Brittany, Centre-Val de Loire, Corsica, Grand Est, Hauts-de-France, Île-de-France, Normandy, Nouvelle-Aquitaine, Occitania, Pays de la Loire, Provence-Alpes-Côte d\'Azur',
        
        'Italy': 'Abruzzo, Aosta Valley, Apulia, Basilicata, Calabria, Campania, Emilia-Romagna, Friuli-Venezia Giulia, Lazio, Liguria, Lombardy, Marche, Molise, Piedmont, Sardinia, Sicily, Trentino-Alto Adige, Tuscany, Umbria, Veneto',
        
        'Spain': 'Andalusia, Aragon, Asturias, Balearic Islands, Basque Country, Canary Islands, Cantabria, Castile and León, Castile-La Mancha, Catalonia, Ceuta, Extremadura, Galicia, La Rioja, Madrid, Melilla, Murcia, Navarre, Valencia',
        
        'Brazil': 'Acre, Alagoas, Amapá, Amazonas, Bahia, Ceará, Distrito Federal, Espírito Santo, Goiás, Maranhão, Mato Grosso, Mato Grosso do Sul, Minas Gerais, Pará, Paraíba, Paraná, Pernambuco, Piauí, Rio de Janeiro, Rio Grande do Norte, Rio Grande do Sul, Rondônia, Roraima, Santa Catarina, São Paulo, Sergipe, Tocantins',
        
        'Mexico': 'Aguascalientes, Baja California, Baja California Sur, Campeche, Chiapas, Chihuahua, Coahuila, Colima, Durango, Guanajuato, Guerrero, Hidalgo, Jalisco, México, Michoacán, Morelos, Nayarit, Nuevo León, Oaxaca, Puebla, Querétaro, Quintana Roo, San Luis Potosí, Sinaloa, Sonora, Tabasco, Tamaulipas, Tlaxcala, Veracruz, Yucatán, Zacatecas',
        
        'Argentina': 'Buenos Aires, Catamarca, Chaco, Chubut, Córdoba, Corrientes, Entre Ríos, Formosa, Jujuy, La Pampa, La Rioja, Mendoza, Misiones, Neuquén, Río Negro, Salta, San Juan, San Luis, Santa Cruz, Santa Fe, Santiago del Estero, Tierra del Fuego, Tucumán',
        
        'India': 'Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal',
        
        'China': 'Anhui, Beijing, Chongqing, Fujian, Gansu, Guangdong, Guangxi, Guizhou, Hainan, Hebei, Heilongjiang, Henan, Hong Kong, Hubei, Hunan, Inner Mongolia, Jiangsu, Jiangxi, Jilin, Liaoning, Macau, Ningxia, Qinghai, Shaanxi, Shandong, Shanghai, Shanxi, Sichuan, Tianjin, Tibet, Xinjiang, Yunnan, Zhejiang',
        
        'Japan': 'Aichi, Akita, Aomori, Chiba, Ehime, Fukui, Fukuoka, Fukushima, Gifu, Gunma, Hiroshima, Hokkaido, Hyogo, Ibaraki, Ishikawa, Iwate, Kagawa, Kagoshima, Kanagawa, Kochi, Kumamoto, Kyoto, Mie, Miyagi, Miyazaki, Nagano, Nagasaki, Nara, Niigata, Oita, Okayama, Okinawa, Osaka, Saga, Saitama, Shiga, Shimane, Shizuoka, Tochigi, Tokushima, Tokyo, Tottori, Toyama, Wakayama, Yamagata, Yamaguchi, Yamanashi',
        
        'Russia': 'Adygea, Altai Krai, Altai Republic, Amur Oblast, Arkhangelsk Oblast, Astrakhan Oblast, Bashkortostan, Belgorod Oblast, Bryansk Oblast, Buryatia, Chechnya, Chelyabinsk Oblast, Chukotka, Chuvashia, Dagestan, Ingushetia, Irkutsk Oblast, Ivanovo Oblast, Jewish Autonomous Oblast, Kabardino-Balkaria, Kaliningrad Oblast, Kalmykia, Kaluga Oblast, Kamchatka Krai, Karachay-Cherkessia, Karelia, Kemerovo Oblast, Khabarovsk Krai, Khakassia, Khanty-Mansi, Kirov Oblast, Komi, Kostroma Oblast, Krasnodar Krai, Krasnoyarsk Krai, Kurgan Oblast, Kursk Oblast, Leningrad Oblast, Lipetsk Oblast, Magadan Oblast, Mari El, Mordovia, Moscow, Moscow Oblast, Murmansk Oblast, Nenets, Nizhny Novgorod Oblast, North Ossetia-Alania, Novgorod Oblast, Novosibirsk Oblast, Omsk Oblast, Orenburg Oblast, Oryol Oblast, Penza Oblast, Perm Krai, Primorsky Krai, Pskov Oblast, Rostov Oblast, Ryazan Oblast, Saint Petersburg, Sakha Republic, Sakhalin Oblast, Samara Oblast, Saratov Oblast, Smolensk Oblast, Stavropol Krai, Sverdlovsk Oblast, Tambov Oblast, Tatarstan, Tomsk Oblast, Tula Oblast, Tuva, Tver Oblast, Tyumen Oblast, Udmurtia, Ulyanovsk Oblast, Vladimir Oblast, Volgograd Oblast, Vologda Oblast, Voronezh Oblast, Yamalo-Nenets, Yaroslavl Oblast, Zabaykalsky Krai',
        
        'Nigeria': 'Abia, Adamawa, Akwa Ibom, Anambra, Bauchi, Bayelsa, Benue, Borno, Cross River, Delta, Ebonyi, Edo, Ekiti, Enugu, Gombe, Imo, Jigawa, Kaduna, Kano, Katsina, Kebbi, Kogi, Kwara, Lagos, Nasarawa, Niger, Ogun, Ondo, Osun, Oyo, Plateau, Rivers, Sokoto, Taraba, Yobe, Zamfara',
        
        'South Africa': 'Eastern Cape, Free State, Gauteng, KwaZulu-Natal, Limpopo, Mpumalanga, Northern Cape, North West, Western Cape',
        
        'Turkey': 'Adana, Adıyaman, Afyonkarahisar, Ağrı, Aksaray, Amasya, Ankara, Antalya, Ardahan, Artvin, Aydın, Balıkesir, Bartın, Batman, Bayburt, Bilecik, Bingöl, Bitlis, Bolu, Burdur, Bursa, Çanakkale, Çankırı, Çorum, Denizli, Diyarbakır, Düzce, Edirne, Elazığ, Erzincan, Erzurum, Eskişehir, Gaziantep, Giresun, Gümüşhane, Hakkâri, Hatay, Iğdır, Isparta, Istanbul, İzmir, Kahramanmaraş, Karabük, Karaman, Kars, Kastamonu, Kayseri, Kırıkkale, Kırklareli, Kırşehir, Kilis, Kocaeli, Konya, Kütahya, Malatya, Manisa, Mardin, Mersin, Muğla, Muş, Nevşehir, Niğde, Ordu, Osmaniye, Rize, Sakarya, Samsun, Siirt, Sinop, Sivas, Şanlıurfa, Şırnak, Tekirdağ, Tokat, Trabzon, Tunceli, Uşak, Van, Yalova, Yozgat, Zonguldak',
        
        'Indonesia': 'Aceh, Bali, Bangka Belitung, Banten, Bengkulu, Central Java, Central Kalimantan, Central Sulawesi, East Java, East Kalimantan, East Nusa Tenggara, Gorontalo, Jakarta, Jambi, Lampung, Maluku, North Kalimantan, North Maluku, North Sulawesi, North Sumatra, Papua, Riau, Riau Islands, South Kalimantan, South Sulawesi, South Sumatra, Southeast Sulawesi, West Java, West Kalimantan, West Nusa Tenggara, West Papua, West Sulawesi, West Sumatra, Yogyakarta'
    }
    
    print(f"\n🌍 Adding territories data for {len(territories_data)} countries...")
    print("=" * 60)
    
    countries_updated = 0
    records_updated = 0
    
    for country_name, territories in territories_data.items():
        # Check if country exists in database
        cursor.execute('SELECT COUNT(*) FROM countries_temporal WHERE name = ?', (country_name,))
        if cursor.fetchone()[0] == 0:
            print(f"⚠️  Country '{country_name}' not found in database - skipping")
            continue
        
        # Update territories for all years of this country
        cursor.execute('UPDATE countries_temporal SET territories = ? WHERE name = ?', (territories, country_name))
        records_updated += cursor.rowcount
        countries_updated += 1
        
        territory_count = len(territories.split(', '))
        print(f"✅ {country_name}: {territory_count} territories/divisions")
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"🎉 TERRITORIES DATA UPDATE COMPLETE!")
    print(f"📊 Countries updated: {countries_updated}")
    print(f"📈 Total records updated: {records_updated}")
    print(f"🏛️ Administrative divisions added for major countries")
    print(f"💡 Note: Each country record now includes its territories/states/provinces")

if __name__ == "__main__":
    add_territories_field() 