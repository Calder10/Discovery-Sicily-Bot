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

from SPARQLWrapper import SPARQLWrapper, JSON
from difflib import SequenceMatcher
import json
import configobj
import simplejson
from bs4 import BeautifulSoup
from datetime import timedelta
from time import perf_counter as pc

config = configobj.ConfigObj('path.b')

"""
Funzione che effettua la il confronto tra due stringhe e restituisce un valore di similarità.
"""
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

"""
Funzione per la lettura del dataset in formato JSON.
"""
def read_dataset():
    path = config['FINAL_DATASET']
    with open(path, "rb") as file:
        return json.load(file)

"""
Funzione per il salvataggio del dataset in un file JSON.
"""
def write_dataset(dataset):
    path = config['FINAL_DATASET_MODIFY']
    with open(path, 'w') as f:
        simplejson.dump(dataset , f ,indent=4, ignore_nan=True)

"""
Funzione che permette di effettuare una query SPARQL e ne restituisce i risultati.
"""
def query_sparql(endpoint, query):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

"""
Funzione che aggiorna le informazioni inerenti ai comuni con quelli di DBPEDIA.
"""
def interlinking_comuni(comune,res_comuni_dbo):    
    for res in res_comuni_dbo['results']['bindings']:
            dbo_citta=res['label']['value'].replace("(Italia)","").replace("(Sicilia)","").replace("(comune)","")
            if(similar(str(comune['Nome Comune']),str(dbo_citta))>0.85):
                comune['dbo_comune'] = res['citta']['value']
                break
"""
Funzione che aggiorna le informazioni inerenti i musei con quelli di CULTURAL ON.
"""
def interlinking_musei(comune,res_musei_cis):
    musei_on = list() 
    for res in res_musei_cis["results"]["bindings"]:
        comune_res=res['nome_comune']['value']
        if(similar(str(comune['Nome Comune']),str(comune_res))>0.85):
            musei_on.append(res)
            
    if(len(musei_on)>0):
        for museo_cis in musei_on:
            for museo_ds in comune['Musei']:
                if(similar(str(museo_cis['nome']['value']),str(museo_ds['Denominazione']))>0.85):
                    museo_ds['cis_museo']=museo_cis['risorsa']['value']
                    museo_ds['Descrizione']=BeautifulSoup(museo_cis['descrizione']['value'], "lxml").text
                    museo_ds['latitudine']=float(museo_cis['latitudine']['value'])
                    museo_ds['longitudine']=float(museo_cis['longitudine']['value'])
                else:
                    aus=dict()
                    aus['Categoria']=museo_cis['categoria']['value']
                    aus['Denominazione']=museo_cis['nome']['value']
                    aus['Indirizzo']=museo_cis['indirizzo']['value']
                    aus['Telefono']=None
                    aus['Biglietto Intero']=None
                    aus['Biglietto Ridotto']=None
                    aus['Note']=None
                    aus['Scheda']=None
                    aus['cis_museo']=museo_cis['risorsa']['value']
                    aus['Descrizione']=BeautifulSoup(museo_cis['descrizione']['value'], "lxml").text
                    aus['latitudine']=float(museo_cis['latitudine']['value'])
                    aus['longitudine']=float(museo_cis['longitudine']['value'])
                    comune['Musei'].append(aus)
                    break
                
                
"""
Funzione che effettua le due query (DBPEDIA e CULTURAL ON) ed effettua il linking.
"""
def interlinking_dataset(dataset): 
    res_comuni_dbo = query_sparql("https://dbpedia.org/sparql",
                       """
                            SELECT DISTINCT ?citta ?label WHERE { 
                                ?citta a dbo:Location ;
                                    dbo:country dbr:Italy .
                                ?citta rdfs:label ?label.
                                FILTER( LANG( ?label) = 'it')
                            }
                       """) 
    res_musei_cis = query_sparql("https://dati.beniculturali.it/sparql",
                       """
                            select distinct ?risorsa ?categoria ?nome ?descrizione ?nome_comune ?indirizzo ?latitudine ?longitudine where { 
                                ?risorsa a cis:CulturalInstituteOrSite .
                                {
                                   ?risorsa rdf:type cis:ArchaeologicalPark .
                                }
                                UNION
                                {
                                  ?risorsa rdf:type cis:Museum .
                                }
                                ?risorsa rdfs:label ?nome .
                                ?risorsa geo:lat ?latitudine .
                                ?risorsa geo:long ?longitudine .
                                ?risorsa dc:type ?categoria.
                                ?risorsa l0:description ?descrizione .
                                ?risorsa  cis:hasSite ?sito . 
                                ?sito cis:siteAddress ?address.
                                ?address clvapit:fullAddress ?indirizzo .
                                ?address clvapit:hasRegion <http://dati.beniculturali.it/mibact/luoghi/resource/Region/Sicilia>.
                                ?address clvapit:hasCity ?comune .
                                ?comune rdfs:label ?nome_comune .
                                filter (lang(?descrizione)="it") .         
                            }
                       """)
    

    for comune in dataset:        
        interlinking_comuni(comune,res_comuni_dbo)
        interlinking_musei(comune,res_musei_cis)
        

"""
Funzione Main
"""    
def main():
    dataset=read_dataset()
    start=pc()
    interlinking_dataset(dataset)
    end=pc()-start
    t=timedelta(seconds=end)
    print("Final dataset saved !")
    print("Ended in",t)
    write_dataset(dataset)


if __name__ == "__main__":
    main()
