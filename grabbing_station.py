# coding: utf-8

import psycopg2
import requests
import zipfile
import io
import xml.etree.ElementTree as et
import json

PRICES_LIST = ["Gazole", "E10", "SP98", "E85", "GPLc", "SP95"]
SERVICES_LIST = ["Restauration à emporter", "Restauration sur place", "Bar", "Station de gonflage", "Lavage",
                 "Vente de gaz domestique (Butane, Propane) ", "Location de véhicule", "Piste poids lourds",
                 "Automate CB", "Lavage automatique", "Lavage manuel", "Vente de fioul domestique",
                 "Vente de pétrole lampant", "Automate CB 24/24", "Relais colis", "Boutique alimentaire",
                 "Boutique non alimentaire", "Carburant additivé", "Services réparation / entretien",
                 "Toilettes publiques", "Wifi", "Aire de camping-cars", "Espace bébé", "Douches", "Bornes électriques"]


def convert_none(val):
    return '' if val is None else val


def extract_prices(pdv):
    prices = {}
    for p in PRICES_LIST:
        prices[p] = None

    for price in pdv.findall("prix"):
        key = str(price.get("nom"))
        if key in prices:
            prices[key] = str(price.get("valeur"))
    return prices


def extract_services(pdv):
    services = {}
    for s in SERVICES_LIST:
        services[s] = False

    for service in pdv.find('services').findall('service'):
        services[service.text] = True
    return services


def export(input_file):
    tree = et.parse(input_file)
    root = tree.getroot()

    buff = []
    for pdv in root.findall('pdv'):

        gas_station_properties = {
            "gasstationid": pdv.get("id"),
            "latitude": float(pdv.get("latitude")) / 100000.0,
            "longitude": float(pdv.get("longitude")) / 100000.0,
            "address": convert_none(pdv.find("adresse").text).replace('"', '').replace('\'', ' '),
            "city": convert_none(pdv.find("ville").text).replace('\'', ' '),
        }
        prices = extract_prices(pdv)
        for p in PRICES_LIST:
            gas_station_properties[p] = prices[p]
        if gas_station_properties["city"] != "":
            buff.append(gas_station_properties)

    return buff


r = requests.get('https://donnees.roulez-eco.fr/opendata/instantane', stream=True)
if r.status_code == 200:
    with zipfile.ZipFile(io.BytesIO(r.content), 'r') as myzip:
        myzip.extractall('tmp')
        myzip.close()
else:
    raise Exception()

data = export('tmp/PrixCarburants_instantane.xml')
print(data)

f = open("credentials.json")
credentials = json.load(f)
f.close()

conn = psycopg2.connect(host=credentials['rds_host'], user=credentials['username'], password=credentials['password'],
                        database=credentials['database'], port=credentials['db_port'],
                        connect_timeout=10)

db_deletion_script = """DROP TABLE IF EXISTS gas_stations;"""
db_creation_script = """CREATE TABLE gas_stations(
            gasstationid BIGINT,
            latitude FLOAT,
            longitude FLOAT,
            address TEXT,
            city TEXT,
            Gazole FLOAT,
            E10 FLOAT,
            SP98 FLOAT,
            E85 FLOAT,
            GPLc FLOAT,
            SP95 FLOAT);"""

columns = ["gasstationid",
           "latitude",
           "longitude",
           "address",
           "city",
           "Gazole",
           "E10",
           "SP98",
           "E85",
           "GPLc",
           "SP95"
           ]

db_populate_script = 'INSERT INTO gas_stations('

for e in columns:
    db_populate_script += e + ', '

db_populate_script = db_populate_script[:-2] + ') VALUES '

for d in data:
    db_populate_script += '('
    for e in columns:
        if d[e] == None:
            db_populate_script += 'null' + ','
        elif e == 'address' or e == 'city':
            db_populate_script += "'" + str(d[e]) + "',"
        else:
            db_populate_script += str(d[e]) + ','
    db_populate_script = db_populate_script[:-1] + '), '

db_populate_script = db_populate_script[:-3] + ');'


with conn.cursor() as cur:
    cur.execute(db_deletion_script)
    print('Deletion')
    cur.execute(db_creation_script)
    print('Creation')
    cur.execute(db_populate_script)
    print('Populate')

conn.commit()
