import requests
import zipfile
import io
import xml.etree.ElementTree as et
import pandas as pd

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
    """Cette fonction permet d'extraire les prix par points de vente"""
    prices = {}
    for p in PRICES_LIST:
        prices[p] = None

    for price in pdv.findall("prix"):
        key = str(price.get("nom"))
        if key in prices:
            prices[key] = str(price.get("valeur"))
    return prices


def export(input_file):
    """Cette fonction tranforme le XML en un dictionnaire avec les informations intéressantes"""
    tree = et.parse(input_file)
    root = tree.getroot()

    buff = []
    for pdv in root.findall('pdv'):

        gas_station_properties = {
            "gasstationid": pdv.get("id"),
            "latitude": float(pdv.get("latitude")) / 100000.0,
            "codepostal": int(pdv.get("cp")),
            "departement": int(pdv.get("cp")) // 1000,
            "longitude": float(pdv.get("longitude")) / 100000.0,
            "address": convert_none(pdv.find("adresse").text).replace('"', '').replace('\'', ' ').title(),
            "city": convert_none(pdv.find("ville").text).replace('\'', ' ').title(),
        }
        prices = extract_prices(pdv)
        for p in PRICES_LIST:
            gas_station_properties[p] = prices[p]
        if gas_station_properties["city"] != "":
            buff.append(gas_station_properties)

    return buff


def export_to_json():
    """Cette fonction requête le site et exporte les stations en Json"""
    r = requests.get('https://donnees.roulez-eco.fr/opendata/instantane', stream=True)
    if r.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(r.content), 'r') as myzip:
            myzip.extractall('tmp')
            myzip.close()
    else:
        raise Exception()
    data = export('tmp/PrixCarburants_instantane.xml')
    df = pd.DataFrame.from_records(data)
    df.to_json('stations.json', orient='records')

if __name__ == '__main__':
    export_to_json()
