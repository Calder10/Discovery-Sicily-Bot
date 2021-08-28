"""
=============================================================================
Università degli Studi Di Palermo
Corso di Laurea Magistrale in Informatica
Anno Accademico 2020/2021
Tecniche per la gestione degli open data
@author: Salvatore Calderaro, Giuseppe Scordato
DiscoverySicily - Bot

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
=============================================================================
"""

import geojson
import simplejson
from tqdm import tqdm
import pandas as pd
import configobj
from time import perf_counter as pc
from datetime import timedelta
from geopy.geocoders import Nominatim
from fuzzywuzzy.fuzz import token_set_ratio

config = configobj.ConfigObj('path.b')
geolocator = Nominatim(user_agent='myapplication')

"""
Funzione che restituisce una lista contenente i comuni siciliani.
"""
def create_cities_list():
    comuni_siciliani=[]
    path=config['ELENCO_COMUNI_ITALIANI']
    data = pd.read_csv(path,sep=",",error_bad_lines=True,encoding = "UTF-8")
    for i, row in data.iterrows():
        if row['Denominazione Regione'] == "Sicilia":
            location = geolocator.geocode(row['Denominazione in italiano'])
            aus=(row['Denominazione in italiano'],row["Denominazione dell'Unità territoriale sovracomunale (valida a fini statistici)"],location.latitude,location.longitude)
            comuni_siciliani.append(aus)
    return comuni_siciliani

"""
Funzione che ritorna una lista contenente i musei siciliani e le relative informazioni.
"""
def create_museum_list():
    path=config['MUSEI_SICILIANI']
    musei_siciliani=[]
    data=pd.read_csv(path,sep=",",error_bad_lines=True,encoding="UTF-8")
    for i,row in data.iterrows():
        musei_siciliani.append(list(row.values))
    return musei_siciliani

"""
Funzione che ritorna una lista contenente i beni immateriali siciliani e le relative informazioni.
"""
def create_beni_immateriali_list():
    path=config['BENI_IMMATERIALI']
    beni_immateriali=[]
    data=pd.read_csv(path,sep=",",error_bad_lines=True,encoding="UTF-8")
    data=data.drop(["id","libro","compilazione"],axis=1)
    for i,row in data.iterrows():
        beni_immateriali.append(list(row.values))
    return beni_immateriali

"""
Funzione che ritorna una lista contenente i castelli siciliani e le relative informazioni.
"""
def create_castles_list():
    path=config['CASTELLI']
    castelli=[]
    with open(path) as f:
        gj = geojson.load(f)
    for feature in gj['features']:
        coordinate=(feature["geometry"]['coordinates'][1],feature["geometry"]['coordinates'][0])
        comune=feature["properties"]['COMUNE']
        cronologia=feature["properties"]['CRONOLOGIA']
        denominazione=feature["properties"]['DENOMINAZI']
        note=feature["properties"]['NOTE_1']
        provincia=feature["properties"]['PROV']
        link=feature["properties"]['WEB_LINK']
        aus=(coordinate,comune,cronologia,denominazione,note,provincia,link)
        castelli.append(aus)
    return castelli

"""
Funzione che ritorna una lista contenente i luoghi del gusto siciliani e le relative informazioni.
"""
def create_luoghi_gusto_list():
    path=config['LUOGHI_GUSTO']
    luoghi_gusto=[]
    with open(path) as f:
        gj = geojson.load(f)
    for feature in gj['features']:
        coordinate=(feature["geometry"]['coordinates'][1],feature["geometry"]['coordinates'][0])
        comune=feature["properties"]['Comuni']
        provincia=feature["properties"]['PROVINCIA']
        elementi=feature["properties"]['elementi']
        note=feature["properties"]['note_1']
        aus=(coordinate,comune,provincia,elementi,note)
        luoghi_gusto.append(aus)
    return luoghi_gusto

"""
Funzione che ritorna una lista contenente le torri costiere siciliane e le relative informazioni.
"""
def create_torri_costiere_list():
    path=config['TORRI_COSTIERE']
    torri_costiere=[]
    with open(path) as f:
        gj = geojson.load(f)
    for feature in gj['features']:
        coordinate=(feature["geometry"]['coordinates'][1],feature["geometry"]['coordinates'][0])
        comune=feature["properties"]['Comune']
        provincia=feature["properties"]['Provincia']
        denominazione=feature["properties"]['DENOM']
        localita=feature["properties"]['Località']
        aus=(coordinate,comune,provincia,denominazione,localita)
        torri_costiere.append(aus)
    return torri_costiere
"""
Funzione che ritorna una lista contenente le torri e le fortezze siciliane e le relative informazioni.
"""
def create_torri_fortezze_list():
    path=config['TORRI_FORTEZZE']
    torri_fortezze=[]
    with open(path) as f:
        gj = geojson.load(f)
    for feature in gj['features']:
        coordinate=(feature["geometry"]['coordinates'][1],feature["geometry"]['coordinates'][0])
        denominazione=feature["properties"]['Denom']
        ubicazione=feature['properties']['Ubicazione']
        note=feature['properties']['note_']
        link=feature['properties']['weblink']
        aus=(coordinate,denominazione,ubicazione,note,link)
        torri_fortezze.append(aus)
    return torri_fortezze

"""
Funzione che che restituisce i musei di un determinato comune preso in input.
"""
def return_museo(comune,musei):
    lista_musei=[]
    for museo in musei:
        aus={}
        score=token_set_ratio(museo[2].lower(),comune.lower())
        if score > 80:
            aus['Categoria']=museo[0]
            aus['Denominazione']=museo[3]
            aus['Indirizzo']=museo[4]
            aus['Telefono']=museo[5]
            aus['Biglietto Intero']=museo[6]
            aus['Biglietto Ridotto']=museo[7]
            aus['Note']=museo[8]
            aus['Scheda']=museo[9]
            lista_musei.append(aus)
    return lista_musei

"""
Funzione che che restituisce i beni immateriali di un determinato comune preso in input.
"""
def return_beni_immateriali(comune,beni_immateriali):
    lista_beni_immateriali=[]
    for bene_imm in beni_immateriali:
        aus={}
        try:
            score=token_set_ratio(bene_imm[2].lower(),comune.lower())
            if score > 80:
                aus['Bene']=bene_imm[0]
                aus['Link']=bene_imm[3]
                aus['Tipo']=bene_imm[4]
                lista_beni_immateriali.append(aus)
        except:
            pass
    return lista_beni_immateriali

"""
Funzione che che restituisce i castelli di un determinato comune preso in input.
"""
def return_castelli(comune,castelli):
    lista_castelli=[]
    for castello in castelli:
        aus={}
        try:
            score=token_set_ratio(castello[1].lower(),comune.lower())
            if score > 80:
                aus['Coordinate']=castello[0]
                aus['Cronologia']=castello[2]
                aus['Denominazione']=castello[3]
                aus['Note']=castello[4]
                aus['Link']=castello[6]
                lista_castelli.append(aus)
        except:
            pass
    return lista_castelli

"""
Funzione che che restituisce i luoghi del gusto di un determinato comune preso in input.
"""
def return_luoghi_gusto(comune,luoghi_gusto):
    lista_luoghi_gusto=[]
    for luogo_gusto in luoghi_gusto:
        aus={}
        try:
            score=token_set_ratio(luogo_gusto[1].lower(),comune.lower())
            if score > 80:
                aus['Coordinate']=luogo_gusto[0]
                aus['Elemento']=luogo_gusto[3]
                aus['Note']=luogo_gusto[4]
                lista_luoghi_gusto.append(aus)
        except:
            pass
    return lista_luoghi_gusto


"""
Funzione che che restituisce le torri costiere determinato comune preso in input.
"""
def return_torri_costiere(comune,torri_costiere):
    lista_torri_costieere=[]
    for torre_costiera in torri_costiere:
        aus={}
        try:
            score=token_set_ratio(torre_costiera[1].lower(),comune.lower())
            if score > 80:
                aus['Coordinate']=torre_costiera[0]
                aus['Denominazione']=torre_costiera[3]
                aus['Località']=torre_costiera[4]
                lista_torri_costieere.append(aus)
        except:
            pass
    return lista_torri_costieere

"""
Funzione che che restituisce le trorri e le fortezze di un determinato comune preso in input.
"""
def return_torri_fortezze(comune,torri_fortezze):
    lista_torri_fortezze=[]
    for torre_fortezza in torri_fortezze:
        aus={}
        try:
            location=geolocator.reverse(str(torre_fortezza[0][0])+","+str(torre_fortezza[0][1]))
            indirizzo=location.raw
            nome_comune=indirizzo['address']['city']
        except:
            try:
                nome_comune=indirizzo['address']['town']
            except:
                nome_comune=indirizzo['address']['county']

        score=token_set_ratio(nome_comune.lower(),comune.lower())
        if score > 80:
            aus['Coordinate']=torre_fortezza[0]
            aus['Denominazione']=torre_fortezza[1]
            aus['Ubicazione']=torre_fortezza[2]
            aus['Note']=torre_fortezza[3]
            aus['Link']=torre_fortezza[4]
            lista_torri_fortezze.append(aus)

    return lista_torri_fortezze

"""
Funzione che effettua il join dei dati e li salva in un file JSON.
"""
def join_data():
    path=config['FINAL_DATASET']
    print("Mining data...")
    print("Creato Comune")
    comuni_siciliani=create_cities_list()
    print("Creato Museo")
    musei_siciliani=create_museum_list()
    print("Creato Beni Immateriali")
    beni_immateriali=create_beni_immateriali_list()   
    print("Creato Castelli") 
    castelli=create_castles_list()
    print("Creato Gusto")
    luoghi_del_gusto=create_luoghi_gusto_list()
    print("Creato Torri Costiere")
    torri_costiere=create_torri_costiere_list()
    print("Creato Fortezze")
    torri_fortezze=create_torri_fortezze_list()

    data=[]
    for i in tqdm(range(len(comuni_siciliani))):
        aus={}
        aus['Nome Comune']=comuni_siciliani[i][0]
        aus['Provincia']=comuni_siciliani[i][1]
        aus['Coordinate']={'Latitudine': comuni_siciliani[i][2],'Longitudine':comuni_siciliani[i][3]}
        musei=return_museo(comuni_siciliani[i][0],musei_siciliani)
        aus['Musei']=musei
        beni_imm=return_beni_immateriali(comuni_siciliani[i][0],beni_immateriali)
        aus['Beni Immateriali']=beni_imm
        lista_castelli=return_castelli(comuni_siciliani[i][0],castelli)
        aus['Castelli']=lista_castelli
        luoghi_gusto=return_luoghi_gusto(comuni_siciliani[i][0],luoghi_del_gusto)
        aus['Luoghi del gusto']=luoghi_gusto
        lista_torri_costiere=return_torri_costiere(comuni_siciliani[i][0],torri_costiere)
        aus['Torri costiere']=lista_torri_costiere
        lista_torri_fortezze=return_torri_fortezze(comuni_siciliani[i][0],torri_fortezze)
        aus['Torri fortezze']=lista_torri_fortezze
        data.append(aus)
        
    with open(path, 'w') as f:
        simplejson.dump(data , f ,indent=4, ignore_nan=True)

"""
Funzione Main
"""
def main():
    print("Dataset creation...")
    start=pc()
    join_data()
    end=pc()-start
    t=timedelta(seconds=end)
    print("Final dataset saved !")
    print("Ended in",t)

if __name__ == "__main__":
    main()