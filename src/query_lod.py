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

import rdflib.graph as g
import configobj
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='myapplication')
config = configobj.ConfigObj('path.b')
path = config['TTL_DATASET']


"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sui musei del comune dato in input.
"""
def info_musei_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()

    query_text = """
                    select distinct ?label ?type ?lat ?long ?description where{
                        """ + comune + """ a dbo:Location ;
                        cis:Museum ?link_museo .
                        ?link_museo cis:institutionalCISName ?label .
                        ?link_museo dc:type ?type .
                        ?link_museo geo:lat ?lat .
                        ?link_museo geo:long ?long .
                        ?link_museo l0:description ?description .                        
                    }
                    
            
            """    
    
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sui musei del comune dato in input.
"""
def info_museirso_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()
    query_text = """
                    select distinct ?label ?type ?address where{
                        """ + comune + """ a dbo:Location ;
                        rso:CulturalProperty ?link_museo .
                        ?link_museo rdfs:label ?label .
                        ?link_museo rso:hasCulturalPropertyType ?type .
                        ?link_museo rso:hasFeatureLocation ?address .            
                    }
            """  
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sui castelli del comune dato in input.
"""
def info_castelli_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()

    query_text = """
                    select distinct ?label ?comment ?date ?lat ?long ?webpage where{
                        """ + comune + """ a dbo:Location ;
                        rso:Castle ?link_castelli .
                        ?link_castelli rdfs:label ?label .
                        ?link_castelli rdfs:comment ?comment .
                        ?link_castelli rso:hasDating ?date .
                        ?link_castelli rso:lat ?lat .
                        ?link_castelli rso:lon ?long .
                        ?link_castelli rso:webPageLink ?webpage .
                    }                   
            
            """    
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sui beni immateriali del comune dato in input.
"""
def info_beni_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()

    query_text = """
                    select distinct ?label ?type ?webpage where{
                        """ + comune + """ a dbo:Location ;
                        rso:IntangibleCulturalProperty ?link_beni .
                        ?link_beni rdfs:label ?label .
                        ?link_beni rso:hasCulturalPropertyType ?type .
                        ?link_beni rso:webPageLink ?webpage .
                    }                   
            
            """    
    
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sui luoghi del gusto del comune dato in input.
"""
def info_gusto_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()

    query_text = """
                    select distinct ?label ?comment where{
                        """ + comune + """ a dbo:Location ;
                        rso:DemoEthnoAnthropologicalHeritage ?link_gusto .
                        ?link_gusto rdfs:label ?label .
                        ?link_gusto rdfs:comment ?comment .
                    }                   
            
            """    
    
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

"""
Funzione che dato un comune in input effettua la query e restituisce le informazioni sulle torri, le fortezze 
e le torri costiere del comune dato in input.
"""
def info_torri_comune(comune):
    result = g.Graph()
    result.parse(path, format="ttl")
    result_query = list()

    query_text = """
                    select distinct ?label ?lat ?long where{
                        """ + comune + """ a dbo:Location ;
                        rso:PointOfInterest ?link_torri .
                        ?link_torri rso:lat ?lat .
                        ?link_torri rso:lon ?long .
                        ?link_torri rdfs:label ?label .
                    }                   
            
            """    
    
    query = result.query(query_text)
    for row in query: 
        aus_list = list()      
        for element in row:           
            stringa = element.replace("\"","").replace("^^<http://www.w3.org/2001/XMLSchema#decimal>","")
            aus_list.append(stringa)
        result_query.append(aus_list)
    return result_query

        
# Prove
if __name__ == '__main__':
    uri_base = "http://www.discoverysicily.it/resource/Comune/"
    comune = "Adrano"
    uri = "<"+uri_base+comune+">"
    #res=info_musei_comune(uri)
    res=info_museirso_comune(uri)
    
    #res = info_castelli_comune(uri)
    #res = info_beni_comune(uri)
    #res = info_gusto_comune(uri)
    #res = info_torri_comune(uri)
    print(res)

    location = geolocator.geocode(res[0][0])
    print("Location",(location.latitude, location.longitude))