#!/usr/bin/env python3
"""
Mapping province italiane con popolazione (ISTAT 2024)
Include città metropolitane, capoluoghi e popolazione per calcolare tassi di penetrazione
"""

# Popolazione province italiane (ISTAT 2024 - dati in migliaia arrotondati)
PROVINCE_POPOLAZIONE = {
    # PIEMONTE
    'Torino': 2230000, 'Vercelli': 166000, 'Novara': 368000, 'Cuneo': 587000,
    'Asti': 210000, 'Alessandria': 410000, 'Biella': 170000, 'Verbano-Cusio-Ossola': 154000,
    # VALLE D'AOSTA
    "Valle d'Aosta": 123000,
    # LOMBARDIA
    'Milano': 3250000, 'Bergamo': 1115000, 'Brescia': 1265000, 'Como': 599000,
    'Cremona': 354000, 'Lecco': 335000, 'Lodi': 230000, 'Mantova': 408000,
    'Monza e Brianza': 875000, 'Pavia': 542000, 'Sondrio': 178000, 'Varese': 890000,
    # TRENTINO-ALTO ADIGE
    'Trento': 545000, 'Bolzano': 535000,
    # VENETO
    'Venezia': 845000, 'Verona': 930000, 'Vicenza': 860000, 'Belluno': 198000,
    'Treviso': 887000, 'Padova': 935000, 'Rovigo': 230000,
    # FRIULI-VENEZIA GIULIA
    'Udine': 524000, 'Gorizia': 138000, 'Trieste': 230000, 'Pordenone': 311000,
    # LIGURIA
    'Genova': 823000, 'Imperia': 212000, 'La Spezia': 217000, 'Savona': 271000,
    # EMILIA-ROMAGNA
    'Bologna': 1020000, 'Ferrara': 340000, 'Forlì-Cesena': 393000, 'Modena': 705000,
    'Parma': 455000, 'Piacenza': 285000, 'Ravenna': 388000, 'Reggio Emilia': 530000,
    'Rimini': 340000,
    # TOSCANA
    'Firenze': 995000, 'Arezzo': 340000, 'Grosseto': 218000, 'Livorno': 330000,
    'Lucca': 385000, 'Massa-Carrara': 190000, 'Pisa': 420000, 'Pistoia': 292000,
    'Prato': 260000, 'Siena': 265000,
    # UMBRIA
    'Perugia': 650000, 'Terni': 220000,
    # MARCHE
    'Ancona': 465000, 'Ascoli Piceno': 202000, 'Fermo': 170000,
    'Macerata': 305000, 'Pesaro e Urbino': 355000,
    # LAZIO
    'Roma': 4250000, 'Frosinone': 475000, 'Latina': 575000, 'Rieti': 153000, 'Viterbo': 310000,
    # ABRUZZO
    "L'Aquila": 295000, 'Teramo': 305000, 'Pescara': 315000, 'Chieti': 380000,
    # MOLISE
    'Campobasso': 215000, 'Isernia': 82000,
    # CAMPANIA
    'Napoli': 2970000, 'Avellino': 405000, 'Benevento': 268000, 'Caserta': 925000, 'Salerno': 1080000,
    # PUGLIA
    'Bari': 1230000, 'Barletta-Andria-Trani': 385000, 'Brindisi': 380000,
    'Foggia': 600000, 'Lecce': 785000, 'Taranto': 555000,
    # BASILICATA
    'Potenza': 355000, 'Matera': 195000,
    # CALABRIA
    'Catanzaro': 350000, 'Cosenza': 690000, 'Crotone': 170000,
    'Reggio Calabria': 530000, 'Vibo Valentia': 155000,
    # SICILIA
    'Palermo': 1230000, 'Agrigento': 415000, 'Caltanissetta': 255000, 'Catania': 1070000,
    'Enna': 158000, 'Messina': 615000, 'Ragusa': 320000, 'Siracusa': 390000, 'Trapani': 420000,
    # SARDEGNA
    'Cagliari': 430000, 'Nuoro': 200000, 'Oristano': 156000, 'Sassari': 490000, 'Sud Sardegna': 340000,
}

# Le 14 Città Metropolitane italiane
CITTA_METROPOLITANE = [
    'Roma', 'Milano', 'Napoli', 'Torino', 'Palermo', 'Bari',
    'Catania', 'Firenze', 'Bologna', 'Genova', 'Venezia',
    'Messina', 'Reggio Calabria', 'Cagliari'
]

# Mapping provincia -> regione (codice)
PROVINCIA_TO_REGIONE = {
    # Piemonte
    'Torino': 'PIE', 'Vercelli': 'PIE', 'Novara': 'PIE', 'Cuneo': 'PIE',
    'Asti': 'PIE', 'Alessandria': 'PIE', 'Biella': 'PIE', 'Verbano-Cusio-Ossola': 'PIE',
    # Valle d'Aosta
    "Valle d'Aosta": 'VDA',
    # Lombardia
    'Milano': 'LOM', 'Bergamo': 'LOM', 'Brescia': 'LOM', 'Como': 'LOM',
    'Cremona': 'LOM', 'Lecco': 'LOM', 'Lodi': 'LOM', 'Mantova': 'LOM',
    'Monza e Brianza': 'LOM', 'Pavia': 'LOM', 'Sondrio': 'LOM', 'Varese': 'LOM',
    # Trentino
    'Trento': 'TRT', 'Bolzano': 'TRB',
    # Veneto
    'Venezia': 'VEN', 'Verona': 'VEN', 'Vicenza': 'VEN', 'Belluno': 'VEN',
    'Treviso': 'VEN', 'Padova': 'VEN', 'Rovigo': 'VEN',
    # Friuli
    'Udine': 'FRI', 'Gorizia': 'FRI', 'Trieste': 'FRI', 'Pordenone': 'FRI',
    # Liguria
    'Genova': 'LIG', 'Imperia': 'LIG', 'La Spezia': 'LIG', 'Savona': 'LIG',
    # Emilia-Romagna
    'Bologna': 'EMI', 'Ferrara': 'EMI', 'Forlì-Cesena': 'EMI', 'Modena': 'EMI',
    'Parma': 'EMI', 'Piacenza': 'EMI', 'Ravenna': 'EMI', 'Reggio Emilia': 'EMI', 'Rimini': 'EMI',
    # Toscana
    'Firenze': 'TOS', 'Arezzo': 'TOS', 'Grosseto': 'TOS', 'Livorno': 'TOS',
    'Lucca': 'TOS', 'Massa-Carrara': 'TOS', 'Pisa': 'TOS', 'Pistoia': 'TOS',
    'Prato': 'TOS', 'Siena': 'TOS',
    # Umbria
    'Perugia': 'UMB', 'Terni': 'UMB',
    # Marche
    'Ancona': 'MAR', 'Ascoli Piceno': 'MAR', 'Fermo': 'MAR', 'Macerata': 'MAR', 'Pesaro e Urbino': 'MAR',
    # Lazio
    'Roma': 'LAZ', 'Frosinone': 'LAZ', 'Latina': 'LAZ', 'Rieti': 'LAZ', 'Viterbo': 'LAZ',
    # Abruzzo
    "L'Aquila": 'ABR', 'Teramo': 'ABR', 'Pescara': 'ABR', 'Chieti': 'ABR',
    # Molise
    'Campobasso': 'MOL', 'Isernia': 'MOL',
    # Campania
    'Napoli': 'CAM', 'Avellino': 'CAM', 'Benevento': 'CAM', 'Caserta': 'CAM', 'Salerno': 'CAM',
    # Puglia
    'Bari': 'PUG', 'Barletta-Andria-Trani': 'PUG', 'Brindisi': 'PUG',
    'Foggia': 'PUG', 'Lecce': 'PUG', 'Taranto': 'PUG',
    # Basilicata
    'Potenza': 'BAS', 'Matera': 'BAS',
    # Calabria
    'Catanzaro': 'CAB', 'Cosenza': 'CAB', 'Crotone': 'CAB', 'Reggio Calabria': 'CAB', 'Vibo Valentia': 'CAB',
    # Sicilia
    'Palermo': 'SIC', 'Agrigento': 'SIC', 'Caltanissetta': 'SIC', 'Catania': 'SIC',
    'Enna': 'SIC', 'Messina': 'SIC', 'Ragusa': 'SIC', 'Siracusa': 'SIC', 'Trapani': 'SIC',
    # Sardegna
    'Cagliari': 'SAR', 'Nuoro': 'SAR', 'Oristano': 'SAR', 'Sassari': 'SAR', 'Sud Sardegna': 'SAR',
}

# Popolazione per regione (aggregata)
REGIONE_POPOLAZIONE = {
    'PIE': 4295000, 'VDA': 123000, 'LOM': 10041000, 'TRT': 545000, 'TRB': 535000,
    'VEN': 4885000, 'FRI': 1203000, 'LIG': 1523000, 'EMI': 4456000, 'TOS': 3695000,
    'UMB': 870000, 'MAR': 1497000, 'LAZ': 5763000, 'ABR': 1295000, 'MOL': 297000,
    'CAM': 5648000, 'PUG': 3935000, 'BAS': 550000, 'CAB': 1895000, 'SIC': 4873000, 'SAR': 1616000
}

# Mapping comuni principali -> provincia (per matching città dal dataset)
# Include varianti di nome comuni
COMUNE_TO_PROVINCIA = {
    # Capoluoghi di regione e città metropolitane
    'ROMA': 'Roma', 'MILANO': 'Milano', 'NAPOLI': 'Napoli', 'TORINO': 'Torino',
    'PALERMO': 'Palermo', 'GENOVA': 'Genova', 'BOLOGNA': 'Bologna', 'FIRENZE': 'Firenze',
    'BARI': 'Bari', 'CATANIA': 'Catania', 'VENEZIA': 'Venezia', 'VERONA': 'Verona',
    'MESSINA': 'Messina', 'PADOVA': 'Padova', 'TRIESTE': 'Trieste', 'BRESCIA': 'Brescia',
    'PARMA': 'Parma', 'TARANTO': 'Taranto', 'PRATO': 'Prato', 'MODENA': 'Modena',
    'REGGIO CALABRIA': 'Reggio Calabria', 'REGGIO DI CALABRIA': 'Reggio Calabria',
    'REGGIO EMILIA': 'Reggio Emilia', "REGGIO NELL'EMILIA": 'Reggio Emilia',
    'PERUGIA': 'Perugia', 'LIVORNO': 'Livorno', 'RAVENNA': 'Ravenna', 'CAGLIARI': 'Cagliari',
    'FOGGIA': 'Foggia', 'RIMINI': 'Rimini', 'SALERNO': 'Salerno', 'FERRARA': 'Ferrara',
    'SASSARI': 'Sassari', 'SIRACUSA': 'Siracusa', 'PESCARA': 'Pescara', 'MONZA': 'Monza e Brianza',
    'BERGAMO': 'Bergamo', 'FORLÌ': 'Forlì-Cesena', 'FORLI': 'Forlì-Cesena',
    'TRENTO': 'Trento', 'VICENZA': 'Vicenza', 'TERNI': 'Terni', 'BOLZANO': 'Bolzano',
    'NOVARA': 'Novara', 'PIACENZA': 'Piacenza', 'ANCONA': 'Ancona', 'ANDRIA': 'Barletta-Andria-Trani',
    'UDINE': 'Udine', 'AREZZO': 'Arezzo', 'LECCE': 'Lecce', 'PESARO': 'Pesaro e Urbino',
    'ALESSANDRIA': 'Alessandria', 'BARLETTA': 'Barletta-Andria-Trani', 'CESENA': 'Forlì-Cesena',
    'LA SPEZIA': 'La Spezia', 'LATINA': 'Latina', 'PISA': 'Pisa', 'CATANZARO': 'Catanzaro',
    'LUCCA': 'Lucca', 'TREVISO': 'Treviso', 'COMO': 'Como', 'BRINDISI': 'Brindisi',
    'BUSTO ARSIZIO': 'Varese', 'VARESE': 'Varese', 'GROSSETO': 'Grosseto', 'CASERTA': 'Caserta',
    'ASTI': 'Asti', 'RAGUSA': 'Ragusa', 'CREMONA': 'Cremona', 'TRAPANI': 'Trapani',
    'COSENZA': 'Cosenza', 'POTENZA': 'Potenza', 'PAVIA': 'Pavia', 'CALTANISSETTA': 'Caltanissetta',
    'VITERBO': 'Viterbo', 'CUNEO': 'Cuneo', 'AVELLINO': 'Avellino', 'BENEVENTO': 'Benevento',
    'GORIZIA': 'Gorizia', 'PORDENONE': 'Pordenone', 'ROVIGO': 'Rovigo', 'BELLUNO': 'Belluno',
    'SIENA': 'Siena', 'PISTOIA': 'Pistoia', 'MASSA': 'Massa-Carrara', 'CARRARA': 'Massa-Carrara',
    'MACERATA': 'Macerata', 'FERMO': 'Fermo', 'ASCOLI PICENO': 'Ascoli Piceno',
    'FROSINONE': 'Frosinone', 'RIETI': 'Rieti', 'TERAMO': 'Teramo', 'CHIETI': 'Chieti',
    "L'AQUILA": "L'Aquila", 'AQUILA': "L'Aquila", 'CAMPOBASSO': 'Campobasso', 'ISERNIA': 'Isernia',
    'CROTONE': 'Crotone', 'VIBO VALENTIA': 'Vibo Valentia', 'MATERA': 'Matera',
    'AGRIGENTO': 'Agrigento', 'ENNA': 'Enna', 'NUORO': 'Nuoro', 'ORISTANO': 'Oristano',
    'LECCO': 'Lecco', 'LODI': 'Lodi', 'MANTOVA': 'Mantova', 'SONDRIO': 'Sondrio',
    'BIELLA': 'Biella', 'VERBANIA': 'Verbano-Cusio-Ossola', 'VERCELLI': 'Vercelli',
    'AOSTA': "Valle d'Aosta", 'IMPERIA': 'Imperia', 'SAVONA': 'Savona',

    # Comuni importanti non capoluogo (per regione)
    # Lombardia
    'SESTO SAN GIOVANNI': 'Milano', 'CINISELLO BALSAMO': 'Milano', 'LEGNANO': 'Milano',
    'SAN DONATO MILANESE': 'Milano', 'COLOGNO MONZESE': 'Milano', 'RHO': 'Milano',
    'GALLARATE': 'Varese', 'SARONNO': 'Varese', 'SEREGNO': 'Monza e Brianza',
    'DESIO': 'Monza e Brianza', 'CANTÙ': 'Como', 'CANTU': 'Como', 'CREMA': 'Cremona',

    # Piemonte
    'MONCALIERI': 'Torino', 'COLLEGNO': 'Torino', 'RIVOLI': 'Torino', 'NICHELINO': 'Torino',
    'SETTIMO TORINESE': 'Torino', 'SAN MAURO TORINESE': 'Torino',

    # Veneto
    'MESTRE': 'Venezia', 'MARGHERA': 'Venezia', 'CHIOGGIA': 'Venezia',
    'SAN DONÀ DI PIAVE': 'Venezia', 'CONEGLIANO': 'Treviso', 'BASSANO DEL GRAPPA': 'Vicenza',
    'SCHIO': 'Vicenza', 'JESOLO': 'Venezia', 'MIRANO': 'Venezia',

    # Emilia-Romagna
    'IMOLA': 'Bologna', 'CARPI': 'Modena', 'SASSUOLO': 'Modena', 'FAENZA': 'Ravenna',
    'LUGO': 'Ravenna', 'CASALECCHIO DI RENO': 'Bologna', 'SAN LAZZARO DI SAVENA': 'Bologna',
    'RICCIONE': 'Rimini', 'CATTOLICA': 'Rimini', 'CESENATICO': 'Forlì-Cesena',

    # Toscana
    'PRATO': 'Prato', 'EMPOLI': 'Firenze', 'SCANDICCI': 'Firenze', 'SESTO FIORENTINO': 'Firenze',
    'CAMPI BISENZIO': 'Firenze', 'PONTEDERA': 'Pisa', 'SAN GIULIANO TERME': 'Pisa',
    'VIAREGGIO': 'Lucca', 'FORTE DEI MARMI': 'Lucca', 'PIETRASANTA': 'Lucca',
    'PIOMBINO': 'Livorno', 'ROSIGNANO MARITTIMO': 'Livorno', 'CECINA': 'Livorno',
    'MONTEVARCHI': 'Arezzo', 'SAN GIOVANNI VALDARNO': 'Arezzo', 'CORTONA': 'Arezzo',
    'MONTECATINI TERME': 'Pistoia', 'MONTEPULCIANO': 'Siena', 'POGGIBONSI': 'Siena',

    # Lazio
    'FIUMICINO': 'Roma', 'GUIDONIA MONTECELIO': 'Roma', 'TIVOLI': 'Roma',
    'CIVITAVECCHIA': 'Roma', 'VELLETRI': 'Roma', 'ANZIO': 'Roma', 'NETTUNO': 'Roma',
    'POMEZIA': 'Roma', 'APRILIA': 'Latina', 'FORMIA': 'Latina', 'TERRACINA': 'Latina',
    'CASSINO': 'Frosinone', 'SORA': 'Frosinone',

    # Campania
    'GIUGLIANO IN CAMPANIA': 'Napoli', 'TORRE DEL GRECO': 'Napoli', 'POZZUOLI': 'Napoli',
    'CASORIA': 'Napoli', 'CASTELLAMMARE DI STABIA': 'Napoli', 'PORTICI': 'Napoli',
    'ERCOLANO': 'Napoli', 'AVERSA': 'Caserta', 'BATTIPAGLIA': 'Salerno', 'CAVA DE\' TIRRENI': 'Salerno',
    'SCAFATI': 'Salerno', 'NOCERA INFERIORE': 'Salerno', 'SORRENTO': 'Napoli',

    # Puglia
    'MOLFETTA': 'Bari', 'ALTAMURA': 'Bari', 'BITONTO': 'Bari', 'BISCEGLIE': 'Barletta-Andria-Trani',
    'TRANI': 'Barletta-Andria-Trani', 'MONOPOLI': 'Bari', 'MARTINA FRANCA': 'Taranto',
    'CERIGNOLA': 'Foggia', 'MANFREDONIA': 'Foggia', 'SAN SEVERO': 'Foggia',
    'NARDÒ': 'Lecce', 'GALLIPOLI': 'Lecce', 'COPERTINO': 'Lecce', 'GALATINA': 'Lecce',

    # Sicilia
    'BAGHERIA': 'Palermo', 'MONREALE': 'Palermo', 'CARINI': 'Palermo',
    'ACIREALE': 'Catania', 'CALTAGIRONE': 'Catania', 'PATERNÒ': 'Catania',
    'MARSALA': 'Trapani', 'MAZARA DEL VALLO': 'Trapani', 'ALCAMO': 'Trapani',
    'VITTORIA': 'Ragusa', 'MODICA': 'Ragusa', 'COMISO': 'Ragusa',
    'AUGUSTA': 'Siracusa', 'NOTO': 'Siracusa', 'AVOLA': 'Siracusa',
    'GELA': 'Caltanissetta', 'BARCELLONA POZZO DI GOTTO': 'Messina', 'MILAZZO': 'Messina',
    'TAORMINA': 'Messina', 'LICATA': 'Agrigento', 'SCIACCA': 'Agrigento',

    # Sardegna
    'QUARTU SANT\'ELENA': 'Cagliari', 'QUARTU SANTELENA': 'Cagliari', 'OLBIA': 'Sassari',
    'ALGHERO': 'Sassari', 'SELARGIUS': 'Cagliari', 'CARBONIA': 'Sud Sardegna',
    'IGLESIAS': 'Sud Sardegna', 'PORTO TORRES': 'Sassari', 'TEMPIO PAUSANIA': 'Sassari',

    # Calabria
    'LAMEZIA TERME': 'Catanzaro', 'RENDE': 'Cosenza', 'CASTROVILLARI': 'Cosenza',
    'CORIGLIANO-ROSSANO': 'Cosenza', 'ROSSANO': 'Cosenza', 'CORIGLIANO': 'Cosenza',
    'VILLA SAN GIOVANNI': 'Reggio Calabria', 'SIDERNO': 'Reggio Calabria',
    'LOCRI': 'Reggio Calabria', 'GIOIA TAURO': 'Reggio Calabria',

    # Friuli-Venezia Giulia
    'MONFALCONE': 'Gorizia', 'SACILE': 'Pordenone', 'CIVIDALE DEL FRIULI': 'Udine',

    # === AGGIUNTE DA DATASET FIGB ===
    # Lombardia
    'SEGRATE': 'Milano', 'CUSANO MILANINO': 'Milano', 'CORSICO': 'Milano',
    'SAN GIULIANO MILANESE': 'Milano', 'ABBIATEGRASSO': 'Milano', 'MAGENTA': 'Milano',
    'MELZO': 'Milano', 'CERNUSCO SUL NAVIGLIO': 'Milano', 'PIOLTELLO': 'Milano',
    'CASALPUSTERLENGO': 'Lodi', 'CODOGNO': 'Lodi', 'VIGEVANO': 'Pavia',
    'VOGHERA': 'Pavia', 'TREVIGLIO': 'Bergamo', 'DESENZANO DEL GARDA': 'Brescia',
    'CHIARI': 'Brescia', 'LUMEZZANE': 'Brescia', 'ROVATO': 'Brescia',
    'ERBA': 'Como', 'MARIANO COMENSE': 'Como',

    # Piemonte
    'PINEROLO': 'Torino', 'CHIERI': 'Torino', 'IVREA': 'Torino', 'CHIVASSO': 'Torino',
    'CARMAGNOLA': 'Torino', 'GRUGLIASCO': 'Torino', 'VENARIA REALE': 'Torino',
    'ORBASSANO': 'Torino', 'CIRIÈ': 'Torino', 'CIRIE': 'Torino', 'ALBA': 'Cuneo',
    'BRA': 'Cuneo', 'FOSSANO': 'Cuneo', 'MONDOVÌ': 'Cuneo', 'MONDOVI': 'Cuneo',
    'SALUZZO': 'Cuneo', 'BORGOMANERO': 'Novara', 'ARONA': 'Novara',
    'CASALE MONFERRATO': 'Alessandria', 'TORTONA': 'Alessandria',

    # Veneto
    'VITTORIO VENETO': 'Treviso', 'CASTELFRANCO VENETO': 'Treviso',
    'MONTEBELLUNA': 'Treviso', 'ODERZO': 'Treviso', 'MOGLIANO VENETO': 'Treviso',
    'VILLAFRANCA DI VERONA': 'Verona', 'SAN BONIFACIO': 'Verona', 'LEGNAGO': 'Verona',
    'THIENE': 'Vicenza', 'VALDAGNO': 'Vicenza', 'ARZIGNANO': 'Vicenza',
    'ABANO TERME': 'Padova', 'PIOVE DI SACCO': 'Padova', 'CITTADELLA': 'Padova',
    'ESTE': 'Padova', 'MONTEGROTTO TERME': 'Padova', 'ADRIA': 'Rovigo',

    # Trentino-Alto Adige
    'ROVERETO': 'Trento', 'RIVA DEL GARDA': 'Trento', 'MERANO': 'Bolzano',
    'BRESSANONE': 'Bolzano', 'BRUNICO': 'Bolzano',

    # Emilia-Romagna
    'CASTELFRANCO EMILIA': 'Modena', 'VIGNOLA': 'Modena', 'MIRANDOLA': 'Modena',
    'FORMIGINE': 'Modena', 'CENTO': 'Ferrara', 'COMACCHIO': 'Ferrara',
    'CERVIA': 'Ravenna', 'SAN GIOVANNI IN PERSICETO': 'Bologna',
    'CASTEL SAN PIETRO TERME': 'Bologna', 'BUDRIO': 'Bologna',
    'FIDENZA': 'Parma', 'SALSOMAGGIORE TERME': 'Parma',

    # Toscana
    'FOLLONICA': 'Grosseto', 'ORBETELLO': 'Grosseto', 'CASTIGLIONE DELLA PESCAIA': 'Grosseto',
    'MONSUMMANO TERME': 'Pistoia', 'QUARRATA': 'Pistoia', 'CASCINA': 'Pisa',
    'SAN MINIATO': 'Pisa', 'VOLTERRA': 'Pisa', 'CAPANNORI': 'Lucca',
    'CAMAIORE': 'Lucca', 'CASTELFIORENTINO': 'Firenze', 'FIGLINE VALDARNO': 'Firenze',

    # Marche
    'FALCONARA MARITTIMA': 'Ancona', 'OSIMO': 'Ancona', 'CHIARAVALLE': 'Ancona',
    'RECANATI': 'Macerata', 'TOLENTINO': 'Macerata', 'PORTO RECANATI': 'Macerata',
    'GROTTAMMARE': 'Ascoli Piceno', 'MONTEPRANDONE': 'Ascoli Piceno',

    # Lazio
    'GROTTAFERRATA': 'Roma', 'FRASCATI': 'Roma', 'ALBANO LAZIALE': 'Roma',
    'CIAMPINO': 'Roma', 'MARINO': 'Roma', 'ARICCIA': 'Roma', 'PALESTRINA': 'Roma',
    'MONTEROTONDO': 'Roma', 'FONTE NUOVA': 'Roma', 'MENTANA': 'Roma',
    'LADISPOLI': 'Roma', 'SANTA MARINELLA': 'Roma', 'CERVETERI': 'Roma',
    'BRACCIANO': 'Roma', 'COLLEFERRO': 'Roma', 'GAETA': 'Latina',

    # Sicilia
    'SAN GREGORIO DI CATANIA': 'Catania', 'TREMESTIERI ETNEO': 'Catania',
    'SAN GIOVANNI LA PUNTA': 'Catania', 'ACI CASTELLO': 'Catania',
    'GIARRE': 'Catania', 'BRONTE': 'Catania', 'MASCALUCIA': 'Catania',
    'MISTERBIANCO': 'Catania', 'BELPASSO': 'Catania', 'GRAVINA DI CATANIA': 'Catania',
    'CASTELVETRANO': 'Trapani', 'ERICE': 'Trapani', 'RIBERA': 'Agrigento',
    'CANICATTI': 'Agrigento', 'FAVARA': 'Agrigento', 'MENFI': 'Agrigento',
    'CEFALÙ': 'Palermo', 'CEFALU': 'Palermo', 'TERMINI IMERESE': 'Palermo',
    'VILLABATE': 'Palermo', 'LENTINI': 'Siracusa', 'FLORIDIA': 'Siracusa',
    'ROSOLINI': 'Siracusa', 'POZZALLO': 'Ragusa', 'ISPICA': 'Ragusa',

    # Sardegna
    'CAPOTERRA': 'Cagliari', 'QUARTU S.ELENA': 'Cagliari', 'ASSEMINI': 'Cagliari',
    'SESTU': 'Cagliari', 'MONSERRATO': 'Cagliari', 'ELMAS': 'Cagliari',
    'SINNAI': 'Cagliari', 'DECIMOMANNU': 'Cagliari', 'VILLASOR': 'Sud Sardegna',
    'VILLACIDRO': 'Sud Sardegna', 'SANLURI': 'Sud Sardegna', 'SAN GAVINO MONREALE': 'Sud Sardegna',
    'GUSPINI': 'Sud Sardegna', 'TORTOLÌ': 'Nuoro', 'TORTOLI': 'Nuoro',
    'MACOMER': 'Nuoro', 'SINISCOLA': 'Nuoro', 'OZIERI': 'Sassari',
    'SORSO': 'Sassari', 'CASTELSARDO': 'Sassari',

    # Liguria
    'BORDIGHERA': 'Imperia', 'ALASSIO': 'Savona', 'FINALE LIGURE': 'Savona',
    'LOANO': 'Savona', 'PIETRA LIGURE': 'Savona', 'VARAZZE': 'Savona',
    'ARENZANO': 'Genova', 'RECCO': 'Genova', 'SANTA MARGHERITA LIGURE': 'Genova',
    'LAVAGNA': 'Genova', 'SARZANA': 'La Spezia', 'LERICI': 'La Spezia',
    'ARCOLA': 'La Spezia', 'DIANO MARINA': 'Imperia', 'TAGGIA': 'Imperia',
    'OSPEDALETTI': 'Imperia', 'VALLECROSIA': 'Imperia',

    # Calabria
    'SCALEA': 'Cosenza', 'PAOLA': 'Cosenza', 'AMANTEA': 'Cosenza',
    'SOVERATO': 'Catanzaro', 'PALMI': 'Reggio Calabria', 'ROSARNO': 'Reggio Calabria',
    'TAURIANOVA': 'Reggio Calabria', 'CIRÒ MARINA': 'Crotone', 'CIRO MARINA': 'Crotone',
    'TROPEA': 'Vibo Valentia', 'PIZZO': 'Vibo Valentia',

    # Puglia
    'FASANO': 'Brindisi', 'OSTUNI': 'Brindisi', 'MESAGNE': 'Brindisi',
    'FRANCAVILLA FONTANA': 'Brindisi', 'ORIA': 'Brindisi', 'CEGLIE MESSAPICA': 'Brindisi',
    'GROTTAGLIE': 'Taranto', 'MANDURIA': 'Taranto', 'MASSAFRA': 'Taranto',
    'CASTELLANA GROTTE': 'Bari', 'CONVERSANO': 'Bari', 'NOCI': 'Bari',
    'RUVO DI PUGLIA': 'Bari', 'CORATO': 'Bari', 'GIOVINAZZO': 'Bari',
    'CANOSA DI PUGLIA': 'Barletta-Andria-Trani', 'MINERVINO MURGE': 'Barletta-Andria-Trani',
    'TRINITAPOLI': 'Barletta-Andria-Trani', 'LUCERA': 'Foggia', 'SAN GIOVANNI ROTONDO': 'Foggia',
    'VIESTE': 'Foggia', 'PESCHICI': 'Foggia', 'MAGLIE': 'Lecce', 'TRICASE': 'Lecce',
    'CASARANO': 'Lecce', 'UGENTO': 'Lecce', 'TAURISANO': 'Lecce',

    # Campania
    'SORRENTO': 'Napoli', 'VICO EQUENSE': 'Napoli', 'PIANO DI SORRENTO': 'Napoli',
    'SANT\'AGNELLO': 'Napoli', 'SANT AGNELLO': 'Napoli', 'MASSA LUBRENSE': 'Napoli',
    'SAN GIUSEPPE VESUVIANO': 'Napoli', 'NOLA': 'Napoli', 'MARIGLIANO': 'Napoli',
    'ACERRA': 'Napoli', 'AFRAGOLA': 'Napoli', 'CAIVANO': 'Napoli',
    'MELITO DI NAPOLI': 'Napoli', 'VILLARICCA': 'Napoli', 'QUARTO': 'Napoli',
    'BACOLI': 'Napoli', 'ISCHIA': 'Napoli', 'CAPRI': 'Napoli', 'PROCIDA': 'Napoli',
    'MARCIANISE': 'Caserta', 'MADDALONI': 'Caserta', 'SANTA MARIA CAPUA VETERE': 'Caserta',
    'CAPUA': 'Caserta', 'CASAGIOVE': 'Caserta', 'CASTEL VOLTURNO': 'Caserta',
    'MONDRAGONE': 'Caserta', 'SESSA AURUNCA': 'Caserta',
    'AGROPOLI': 'Salerno', 'EBOLI': 'Salerno', 'PONTECAGNANO FAIANO': 'Salerno',
    'PAGANI': 'Salerno', 'SARNO': 'Salerno', 'ANGRI': 'Salerno', 'VIETRI SUL MARE': 'Salerno',
    'MAIORI': 'Salerno', 'POSITANO': 'Salerno', 'AMALFI': 'Salerno', 'RAVELLO': 'Salerno',
    'ARIANO IRPINO': 'Avellino', 'MONTELLA': 'Avellino', 'MERCOGLIANO': 'Avellino',

    # Abruzzo
    'FRANCAVILLA AL MARE': 'Chieti', 'ORTONA': 'Chieti', 'SAN SALVO': 'Chieti',
    'SILVI': 'Teramo', 'TORTORETO': 'Teramo', 'ALBA ADRIATICA': 'Teramo',
    'PINETO': 'Teramo', 'MARTINSICURO': 'Teramo', 'SANSEVERINO MARCHE': 'Macerata',

    # Basilicata
    'MELFI': 'Potenza', 'VENOSA': 'Potenza', 'RIONERO IN VULTURE': 'Potenza',
    'LAURIA': 'Potenza', 'POLICORO': 'Matera', 'PISTICCI': 'Matera',
    'BERNALDA': 'Matera', 'MONTESCAGLIOSO': 'Matera',

    # Umbria
    'ASSISI': 'Perugia', 'BASTIA UMBRA': 'Perugia', 'CASTIGLIONE DEL LAGO': 'Perugia',
    'CORCIANO': 'Perugia', 'MARSCIANO': 'Perugia', 'TODI': 'Perugia',

    # Liguria
    'SAN REMO': 'Imperia', 'SANREMO': 'Imperia', 'RAPALLO': 'Genova', 'CHIAVARI': 'Genova',
    'SESTRI LEVANTE': 'Genova', 'ALBENGA': 'Savona', 'VENTIMIGLIA': 'Imperia',

    # Abruzzo
    "MONTESILVANO": 'Pescara', "VASTO": 'Chieti', "LANCIANO": 'Chieti',
    "AVEZZANO": "L'Aquila", "SULMONA": "L'Aquila", "GIULIANOVA": 'Teramo', "ROSETO DEGLI ABRUZZI": 'Teramo',

    # Umbria
    'FOLIGNO': 'Perugia', 'CITTÀ DI CASTELLO': 'Perugia', 'CITTA DI CASTELLO': 'Perugia',
    'SPOLETO': 'Perugia', 'GUBBIO': 'Perugia', 'ORVIETO': 'Terni', 'NARNI': 'Terni',

    # Marche
    'JESI': 'Ancona', 'FABRIANO': 'Ancona', 'SENIGALLIA': 'Ancona',
    'FANO': 'Pesaro e Urbino', 'URBINO': 'Pesaro e Urbino', 'CIVITANOVA MARCHE': 'Macerata',
    'SAN BENEDETTO DEL TRONTO': 'Ascoli Piceno', 'PORTO SANT\'ELPIDIO': 'Fermo',
}


def get_provincia_from_city(city_name):
    """
    Dato il nome di una città, restituisce la provincia di appartenenza.
    Restituisce None se non trovata.
    """
    if pd.isna(city_name) or city_name == '':
        return None

    city_upper = str(city_name).upper().strip()

    # Cerca prima nel mapping diretto
    if city_upper in COMUNE_TO_PROVINCIA:
        return COMUNE_TO_PROVINCIA[city_upper]

    # Cerca varianti (rimuovi accenti comuni, etc.)
    city_clean = city_upper.replace("'", "").replace("-", " ")
    if city_clean in COMUNE_TO_PROVINCIA:
        return COMUNE_TO_PROVINCIA[city_clean]

    # Se il nome città corrisponde a una provincia, usa quella
    for prov in PROVINCE_POPOLAZIONE.keys():
        if prov.upper() == city_upper:
            return prov

    return None


def get_regione_from_provincia(provincia):
    """Restituisce il codice regione data la provincia"""
    return PROVINCIA_TO_REGIONE.get(provincia)


def is_citta_metropolitana(provincia):
    """Verifica se la provincia è una città metropolitana"""
    return provincia in CITTA_METROPOLITANE


def get_popolazione_provincia(provincia):
    """Restituisce la popolazione della provincia"""
    return PROVINCE_POPOLAZIONE.get(provincia, 0)


def get_popolazione_regione(regione_code):
    """Restituisce la popolazione della regione"""
    return REGIONE_POPOLAZIONE.get(regione_code, 0)


def calcola_tasso_penetrazione(tesserati, popolazione):
    """Calcola tesserati per 100.000 abitanti"""
    if popolazione <= 0:
        return 0
    return (tesserati / popolazione) * 100000


# Import pandas per type hints
try:
    import pandas as pd
except ImportError:
    pd = None
