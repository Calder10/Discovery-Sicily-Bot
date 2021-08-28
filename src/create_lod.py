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

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, OWL, XSD, DC,RDFS
import re
import json
import configobj
from fuzzywuzzy.fuzz import token_set_ratio

config = configobj.ConfigObj('path.b')

"""
Funzione per la lettura del dataset in formato JSON.
"""
def read_file():
    path = config['FINAL_DATASET_MODIFY']
    with open(path, "rb") as file:
        return json.load(file)


"""
Funzione per la creazione del dataset in formato ttl.
"""
def create_lod(graph):
    path=config['TTL_DATASET']
    graph.serialize(destination=path, format='turtle')

"""
Funzione che controlla se per una risorsa (luoghi del gusto) il campo noten è ripetuto più volte.
"""
def duplicate_control(list_check, note):
    flag = True
    for x in list_check:
        score=token_set_ratio(x,note)
        if score>95:
            flag = False
    return flag

"""
Funziome per la creazione del dataset ttl.
"""
def create_graph(data):
    g = Graph()
    dso = Namespace("http://www.discoverysicily.it/ontology/")
    cis = Namespace("http://dati.beniculturali.it/cis/")
    dbo = Namespace("http://dbpedia.org/ontology/")
    rso = Namespace("https://dati.regione.sicilia.it/onto/regionesiciliana/")
    dbp = Namespace("http://dbpedia.org/property/")
    geo = Namespace("http://www.w3.org/2003/01/geo/")
    l0 = Namespace("https://w3id.org/italia/onto/l0/")
    g.bind("cis", cis)
    g.bind("l0", l0)
    g.bind("geo", geo)
    g.bind("dso", dso)
    g.bind("dbo", dbo)
    g.bind("dbp", dbp)
    g.bind("rso", rso)
    g.bind("owl", OWL)
    g.bind("dc", DC)

    ds_comune_uri = "http://www.discoverysicily.it/resource/Comune/"
    ds_museo_uri = "http://www.discoverysicily.it/resource/Museo/"
    ds_museorso_uri = "http://www.discoverysicily.it/resource/MuseoRSO/"
    ds_castello_uri = "http://www.discoverysicily.it/resource/Castello/"
    ds_bene_imm_uri = "http://www.discoverysicily.it/resource/BeneImmmateriale/"
    ds_luogo_del_gusto = "http://www.discoverysicily.it/resource/LuogoDelGusto/"
    ds_torre_uri = "http://www.discoverysicily.it/resource/Torre/"
    list_check = list()
    counter=1
    for comune in data:
        nc=comune['Nome Comune'].replace(" ","_").replace('\'',"").replace(".","")
        try:
            g.add([URIRef(ds_comune_uri+nc), RDF.type, dbo.Location])
            g.add([URIRef(ds_comune_uri+nc), dbo.lat, Literal(comune["Coordinate"]["Latitudine"], datatype=XSD.double)])
            g.add([URIRef(ds_comune_uri+nc), dbo.long, Literal(comune["Coordinate"]["Longitudine"], datatype=XSD.double)])
            
            try:
                g.add([URIRef(ds_comune_uri+nc), dbp.name, Literal(comune["Nome Comune"])])
                g.add([URIRef(ds_comune_uri+nc), dbp.metropolitanCity, Literal(comune["Provincia"])])
            except:
                g.add([URIRef(ds_comune_uri+nc), dbo.provincie, Literal(comune["Provincia"])])
                pass                       
            
        except:
            pass
        
        for museo in comune['Musei']:
            nm=museo["Denominazione"].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")           
            try:
                if museo['cis_museo'] != "":
                    g.add([URIRef(ds_comune_uri+nc), cis.Museum, URIRef(ds_museo_uri+nm)])
                    g.add([URIRef(ds_museo_uri+nm), RDF.type, cis.Museum])
                    g.add([URIRef(ds_museo_uri+nm), cis.institutionalCISName, Literal(museo['Denominazione'])])
                    g.add([URIRef(ds_museo_uri+nm), geo.lat, Literal(museo['latitudine'],datatype=XSD.double)])
                    g.add([URIRef(ds_museo_uri+nm), geo.long, Literal(museo['longitudine'],datatype=XSD.double)])
                    g.add([URIRef(ds_museo_uri+nm), DC.type, Literal(museo['Categoria'])])
                    g.add([URIRef(ds_museo_uri+nm), l0.description, Literal(museo['Descrizione'])])
                    g.add([URIRef(ds_comune_uri+nc), rso.CulturalProperty, URIRef(ds_museorso_uri+nm)])

            except:
                g.add([URIRef(ds_comune_uri+nc), rso.CulturalProperty, URIRef(ds_museorso_uri+nm)])
                g.add([URIRef(ds_museorso_uri+nm), RDF.type, rso.CulturalProperty])
                g.add([URIRef(ds_museorso_uri+nm), RDFS.label, Literal(museo['Denominazione'])])
                g.add([URIRef(ds_museorso_uri+nm), rso.hasFeatureLocation, Literal(museo['Indirizzo'])])
                g.add([URIRef(ds_museorso_uri+nm), rso.hasCulturalPropertyType, Literal(museo['Categoria'])])


        for castello in comune['Castelli']:
            ncast = castello['Denominazione'].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")             
            try:
                g.add([URIRef(ds_comune_uri+nc), rso.Castle, URIRef(ds_castello_uri+ncast)])
                g.add([URIRef(ds_castello_uri+ncast), RDF.type, rso.Castle])
                g.add([URIRef(ds_castello_uri+ncast), RDFS.label, Literal(castello['Denominazione'])])
                g.add([URIRef(ds_castello_uri+ncast), RDFS.comment, Literal(castello['Note'])])
                g.add([URIRef(ds_castello_uri+ncast), rso.webPageLink, Literal(castello['Link'])])
                g.add([URIRef(ds_castello_uri+ncast), rso.hasDating, Literal(castello['Cronologia'])])
                g.add([URIRef(ds_castello_uri+ncast),rso.lat,Literal(castello['Coordinate'][0],datatype=XSD.decimal)])
                g.add([URIRef(ds_castello_uri+ncast),rso.lon,Literal(castello['Coordinate'][1],datatype=XSD.decimal)])
            except:
                pass
        
        for bene in comune['Beni Immateriali']:
            nbene = bene['Bene'].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")
            try:
                g.add([URIRef(ds_comune_uri+nc), rso.IntangibleCulturalProperty, URIRef(ds_bene_imm_uri+nbene+str(counter))])
                g.add([URIRef(ds_bene_imm_uri+nbene+str(counter)), RDF.type, rso.IntangibleCulturalProperty])
                g.add([URIRef(ds_bene_imm_uri+nbene+str(counter)), RDFS.label, Literal(bene['Bene'])])
                g.add([URIRef(ds_bene_imm_uri+nbene+str(counter)), rso.webPageLink, Literal(bene['Link'])])
                g.add([URIRef(ds_bene_imm_uri+nbene+str(counter)), rso.hasCulturalPropertyType, Literal(bene['Tipo'])])
            except:
                pass
            
        
        
        for luogo_gusto in comune['Luoghi del gusto']:
            nlg=luogo_gusto['Elemento'].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")
            try:
                g.add([URIRef(ds_comune_uri+nc), rso.DemoEthnoAnthropologicalHeritage, URIRef(ds_luogo_del_gusto+nlg)])
                g.add([URIRef(ds_luogo_del_gusto+nlg), RDF.type, rso.DemoEthnoAnthropologicalHeritage])
                g.add([URIRef(ds_luogo_del_gusto+nlg), RDFS.label, Literal(luogo_gusto['Elemento'])])
                if duplicate_control(list_check,luogo_gusto['Note']):
                    g.add([URIRef(ds_luogo_del_gusto+nlg), RDFS.comment, Literal(luogo_gusto['Note'])])
                    list_check.append(luogo_gusto['Note'])
            except:
                pass
        
        for torre in comune['Torri fortezze']:
            twr=torre['Denominazione'].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")
            try:
                g.add([URIRef(ds_comune_uri+nc), rso.PointOfInterest, URIRef(ds_torre_uri+twr)])
                g.add([URIRef(ds_torre_uri+twr), RDF.type, rso.PointOfInterest])
                g.add([URIRef(ds_torre_uri+twr), RDFS.label, Literal(torre['Denominazione'])])
                g.add([URIRef(ds_torre_uri+twr), RDFS.comment, Literal(torre['Note'])])
                g.add([URIRef(ds_torre_uri+twr), rso.webPageLink, Literal(torre['Link'])])
                g.add([URIRef(ds_torre_uri+twr), rso.lat,Literal(torre['Coordinate'][0],datatype=XSD.decimal)])
                g.add([URIRef(ds_torre_uri+twr), rso.lon,Literal(torre['Coordinate'][1],datatype=XSD.decimal)])
            except:
                pass
        
        for torre in comune['Torri costiere']:
            twr=torre['Denominazione'].replace(" ","_").replace('\'',"").replace('\"',"").replace(".","")
            try:
                g.add([URIRef(ds_comune_uri+nc), rso.PointOfInterest, URIRef(ds_torre_uri+twr)])
                g.add([URIRef(ds_torre_uri+twr), RDF.type, rso.PointOfInterest])
                g.add([URIRef(ds_torre_uri+twr), RDFS.label, Literal(torre['Denominazione'])])
                g.add([URIRef(ds_torre_uri+twr), rso.lat,Literal(torre['Coordinate'][0],datatype=XSD.decimal)])
                g.add([URIRef(ds_torre_uri+twr), rso.lon,Literal(torre['Coordinate'][1],datatype=XSD.decimal)])
            except:
                pass
        counter+=1
        
    return g

"""
Funzione main
"""
def main():
    data=read_file()
    g=create_graph(data)
    create_lod(g)


if __name__=="__main__":
    main()