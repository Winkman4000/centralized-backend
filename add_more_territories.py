#!/usr/bin/env python3

import sqlite3

def add_more_territories():
    """Add territories data for many more countries"""
    
    # Comprehensive territories data for more countries
    territories_data = {
        # European Countries
        'Austria': 'Burgenland, Carinthia, Lower Austria, Upper Austria, Salzburg, Styria, Tyrol, Vorarlberg, Vienna',
        
        'Belgium': 'Antwerp, East Flanders, Flemish Brabant, Hainaut, Liège, Limburg, Luxembourg, Namur, Walloon Brabant, West Flanders, Brussels-Capital Region',
        
        'Switzerland': 'Aargau, Appenzell Ausserrhoden, Appenzell Innerrhoden, Basel-Landschaft, Basel-Stadt, Bern, Fribourg, Geneva, Glarus, Graubünden, Jura, Lucerne, Neuchâtel, Nidwalden, Obwalden, Schaffhausen, Schwyz, Solothurn, St. Gallen, Thurgau, Ticino, Uri, Valais, Vaud, Zug, Zurich',
        
        'Netherlands': 'Drenthe, Flevoland, Friesland, Gelderland, Groningen, Limburg, North Brabant, North Holland, Overijssel, South Holland, Utrecht, Zeeland',
        
        'Poland': 'Greater Poland, Kuyavian-Pomeranian, Lesser Poland, Lodz, Lower Silesian, Lublin, Lubusz, Masovian, Opole, Podlaskie, Pomeranian, Silesian, Subcarpathian, Swietokrzyskie, Warmian-Masurian, West Pomeranian',
        
        'Czech Republic': 'Central Bohemian, South Bohemian, Plzen, Karlovy Vary, Usti nad Labem, Liberec, Hradec Kralove, Pardubice, Vysocina, South Moravian, Olomouc, Moravian-Silesian, Zlin, Prague',
        
        'Romania': 'Alba, Arad, Arges, Bacau, Bihor, Bistrita-Nasaud, Botosani, Braila, Brasov, Buzau, Calarasi, Caras-Severin, Cluj, Constanta, Covasna, Dambovita, Dolj, Galati, Giurgiu, Gorj, Harghita, Hunedoara, Ialomita, Iasi, Ilfov, Maramures, Mehedinti, Mures, Neamt, Olt, Prahova, Salaj, Satu Mare, Sibiu, Suceava, Teleorman, Timis, Tulcea, Vaslui, Valcea, Vrancea, Bucharest',
        
        'Ukraine': 'Cherkasy, Chernihiv, Chernivtsi, Dnipropetrovsk, Donetsk, Ivano-Frankivsk, Kharkiv, Kherson, Khmelnytskyi, Kiev, Kirovohrad, Luhansk, Lviv, Mykolaiv, Odessa, Poltava, Rivne, Sumy, Ternopil, Vinnytsia, Volyn, Zakarpattia, Zaporizhzhia, Zhytomyr, Crimea',
        
        'Sweden': 'Blekinge, Dalarna, Gavleborg, Gotland, Halland, Jamtland, Jonkoping, Kalmar, Kronoberg, Norrbotten, Orebro, Ostergotland, Skane, Sodermanland, Stockholm, Uppsala, Varmland, Vasterbotten, Vasternorrland, Vastmanland, Vastra Gotaland',
        
        'Norway': 'Agder, Innlandet, More og Romsdal, Nordland, Oslo, Rogaland, Troms og Finnmark, Trondelag, Vestfold og Telemark, Vestland, Viken',
        
        'Finland': 'Aland, Central Finland, Central Ostrobothnia, Kainuu, Kanta-Hame, Karelia, Kymenlaakso, Lapland, North Karelia, North Ostrobothnia, North Savo, Ostrobothnia, Paijat-Hame, Pirkanmaa, Satakunta, South Karelia, South Ostrobothnia, South Savo, Tavastia Proper, Uusimaa',
        
        'Denmark': 'Capital Region, Central Denmark, North Denmark, Region Zealand, Southern Denmark',
        
        'Ireland': 'Carlow, Cavan, Clare, Cork, Donegal, Dublin, Galway, Kerry, Kildare, Kilkenny, Laois, Leitrim, Limerick, Longford, Louth, Mayo, Meath, Monaghan, Offaly, Roscommon, Sligo, Tipperary, Waterford, Westmeath, Wexford, Wicklow',
        
        # African Countries
        'Egypt': 'Alexandria, Aswan, Asyut, Beheira, Beni Suef, Cairo, Dakahlia, Damietta, Fayyum, Gharbia, Giza, Ismailia, Kafr el-Sheikh, Luxor, Matruh, Minya, Monufia, New Valley, North Sinai, Port Said, Qalyubia, Qena, Red Sea, Sharqia, Sohag, South Sinai, Suez',
        
        'South Africa': 'Eastern Cape, Free State, Gauteng, KwaZulu-Natal, Limpopo, Mpumalanga, Northern Cape, North West, Western Cape',
        
        'Morocco': 'Beni Mellal-Khenifra, Casablanca-Settat, Draa-Tafilalet, Fes-Meknes, Guelmim-Oued Noun, Laayoune-Sakia El Hamra, Marrakech-Safi, Oriental, Rabat-Sale-Kenitra, Souss-Massa, Tanger-Tetouan-Al Hoceima, Dakhla-Oued Ed-Dahab',
        
        'Algeria': 'Adrar, Ain Defla, Ain Temouchent, Algiers, Annaba, Batna, Bechar, Bejaia, Biskra, Blida, Bordj Bou Arreridj, Bouira, Boumerdes, Chlef, Constantine, Djelfa, El Bayadh, El Oued, El Tarf, Ghardaia, Guelma, Illizi, Jijel, Khenchela, Laghouat, Mascara, Medea, Mila, Mostaganem, Msila, Naama, Oran, Ouargla, Oum el Bouaghi, Relizane, Saida, Setif, Sidi Bel Abbes, Skikda, Souk Ahras, Tamanrasset, Tebessa, Tiaret, Tindouf, Tipaza, Tissemsilt, Tizi Ouzou, Tlemcen',
        
        'Kenya': 'Baringo, Bomet, Bungoma, Busia, Elgeyo-Marakwet, Embu, Garissa, Homa Bay, Isiolo, Kajiado, Kakamega, Kericho, Kiambu, Kilifi, Kirinyaga, Kisii, Kisumu, Kitui, Kwale, Laikipia, Lamu, Machakos, Makueni, Mandera, Marsabit, Meru, Migori, Mombasa, Murang\'a, Nairobi, Nakuru, Nandi, Narok, Nyamira, Nyandarua, Nyeri, Samburu, Siaya, Taita-Taveta, Tana River, Tharaka-Nithi, Trans Nzoia, Turkana, Uasin Gishu, Vihiga, Wajir, West Pokot',
        
        # Asian Countries
        'Afghanistan': 'Badakhshan, Badghis, Baghlan, Balkh, Bamyan, Daykundi, Farah, Faryab, Ghazni, Ghor, Helmand, Herat, Jowzjan, Kabul, Kandahar, Kapisa, Khost, Kunar, Kunduz, Laghman, Logar, Nangarhar, Nimroz, Nuristan, Paktia, Paktika, Panjshir, Parwan, Samangan, Sar-e Pol, Takhar, Uruzgan, Wardak, Zabul',
        
        'Bangladesh': 'Barisal, Chittagong, Dhaka, Khulna, Mymensingh, Rajshahi, Rangpur, Sylhet',
        
        'Pakistan': 'Balochistan, Khyber Pakhtunkhwa, Punjab, Sindh, Azad Kashmir, Gilgit-Baltistan, Islamabad Capital Territory',
        
        'Sri Lanka': 'Central, Eastern, North Central, Northern, North Western, Sabaragamuwa, Southern, Uva, Western',
        
        'Nepal': 'Bagmati, Gandaki, Karnali, Lumbini, Province No. 1, Province No. 2, Sudurpashchim',
        
        'Myanmar': 'Ayeyarwady, Bago, Chin, Kachin, Kayah, Kayin, Magway, Mandalay, Mon, Naypyidaw, Rakhine, Sagaing, Shan, Tanintharyi, Yangon',
        
        'Cambodia': 'Banteay Meanchey, Battambang, Kampong Cham, Kampong Chhnang, Kampong Speu, Kampong Thom, Kampot, Kandal, Kep, Koh Kong, Kratie, Mondulkiri, Oddar Meanchey, Pailin, Phnom Penh, Preah Sihanouk, Preah Vihear, Prey Veng, Pursat, Ratanakiri, Siem Reap, Stung Treng, Svay Rieng, Takeo, Tbong Khmum',
        
        # Middle Eastern Countries
        'Iran': 'Alborz, Ardabil, Bushehr, Chaharmahal and Bakhtiari, East Azerbaijan, Fars, Gilan, Golestan, Hamadan, Hormozgan, Ilam, Isfahan, Kerman, Kermanshah, Khuzestan, Kohgiluyeh and Boyer-Ahmad, Kurdistan, Lorestan, Markazi, Mazandaran, North Khorasan, Qazvin, Qom, Razavi Khorasan, Semnan, Sistan and Baluchestan, South Khorasan, Tehran, West Azerbaijan, Yazd, Zanjan',
        
        'Iraq': 'Al Anbar, Babil, Baghdad, Basra, Dhi Qar, Al-Qadisiyyah, Diyala, Dohuk, Erbil, Karbala, Kirkuk, Maysan, Muthanna, Najaf, Nineveh, Saladin, Sulaymaniyah, Wasit',
        
        'Saudi Arabia': 'Al Bahah, Al Hudud ash Shamaliyah, Al Jawf, Al Madinah, Al Qasim, Ar Riyad, Ash Sharqiyah, Asir, Hail, Jazan, Makkah, Najran, Tabuk',
        
        # Latin American Countries
        'Chile': 'Arica y Parinacota, Tarapaca, Antofagasta, Atacama, Coquimbo, Valparaiso, Santiago, O\'Higgins, Maule, Nuble, Biobio, Araucania, Los Rios, Los Lagos, Aysen, Magallanes',
        
        'Colombia': 'Amazonas, Antioquia, Arauca, Atlantico, Bolivar, Boyaca, Caldas, Caqueta, Casanare, Cauca, Cesar, Choco, Cordoba, Cundinamarca, Guainia, Guaviare, Huila, La Guajira, Magdalena, Meta, Narino, Norte de Santander, Putumayo, Quindio, Risaralda, San Andres y Providencia, Santander, Sucre, Tolima, Valle del Cauca, Vaupes, Vichada, Bogota',
        
        'Peru': 'Amazonas, Ancash, Apurimac, Arequipa, Ayacucho, Cajamarca, Callao, Cusco, Huancavelica, Huanuco, Ica, Junin, La Libertad, Lambayeque, Lima, Loreto, Madre de Dios, Moquegua, Pasco, Piura, Puno, San Martin, Tacna, Tumbes, Ucayali',
        
        'Venezuela': 'Amazonas, Anzoategui, Apure, Aragua, Barinas, Bolivar, Carabobo, Cojedes, Delta Amacuro, Falcon, Guarico, Lara, Merida, Miranda, Monagas, Nueva Esparta, Portuguesa, Sucre, Tachira, Trujillo, Vargas, Yaracuy, Zulia, Capital District',
        
        'Ecuador': 'Azuay, Bolivar, Canar, Carchi, Chimborazo, Cotopaxi, El Oro, Esmeraldas, Galapagos, Guayas, Imbabura, Loja, Los Rios, Manabi, Morona-Santiago, Napo, Orellana, Pastaza, Pichincha, Santa Elena, Santo Domingo de los Tsachilas, Sucumbios, Tungurahua, Zamora-Chinchipe'
    }
    
    conn = sqlite3.connect('geography_temporal.db')
    cursor = conn.cursor()
    
    print(f"🏛️ Adding territories data for {len(territories_data)} more countries...")
    print("=" * 60)
    
    countries_updated = 0
    records_updated = 0
    
    for country_name, territories in territories_data.items():
        # Check if country exists in database
        cursor.execute('SELECT COUNT(*) FROM countries_temporal WHERE name = ?', (country_name,))
        if cursor.fetchone()[0] == 0:
            print(f"⚠️  Country '{country_name}' not found in database - skipping")
            continue
        
        # Check if country already has territories data
        cursor.execute('SELECT COUNT(*) FROM countries_temporal WHERE name = ? AND territories IS NOT NULL', (country_name,))
        if cursor.fetchone()[0] > 0:
            print(f"ℹ️  Country '{country_name}' already has territories data - skipping")
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
    print(f"🎉 ADDITIONAL TERRITORIES DATA UPDATE COMPLETE!")
    print(f"📊 Countries updated: {countries_updated}")
    print(f"📈 Total records updated: {records_updated}")
    print(f"🌍 Now covering administrative divisions across all continents")

if __name__ == "__main__":
    add_more_territories() 