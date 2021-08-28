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

import time
import telepot
import json
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.distance import great_circle
import query_lod as ql
import configobj
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='myapplication')
config = configobj.ConfigObj('path.b')

MAX_TEXT = 3000

URI_BASE_COMUNE = "http://www.discoverysicily.it/resource/Comune/"
URI_BASE_MUSEO = "http://www.discoverysicily.it/resource/Museo/"
URI_BASE_CASTELLO = "http://www.discoverysicily.it/resource/Castello/"
URI_BASE_BENE = "http://www.discoverysicily.it/resource/BeneImmmateriale/"
URI_BASE_GUSTO = "http://www.discoverysicily.it/resource/LuogoDelGusto/"
URI_BASE_TORRE = "http://www.discoverysicily.it/resource/Torre/"

last_keybords = {}

"""
Funzione per la lettura del dataset in fornato JSON.
"""
def read_dataset():
    path = config['FINAL_DATASET_MODIFY']
    with open(path, "rb") as file:
        return json.load(file)

"""
Funzione che analizza la posizone inviata dall'utente.
"""
def send_comuni_geo(bot, updates):
    last_positions[updates["chat"]["id"]] = (updates['location']["latitude"], updates['location']["longitude"])   
    mypos = (updates['location']["latitude"], updates['location']["longitude"])
    print(mypos)
    search_place_near(2000,mypos,bot, updates, False)

"""
Funzioene che analizza il messagio inviato dall'utente e restituisce un bottone con il 
nome del comune e la relativa geolocalizzazione o un messaggio di errore.
"""
def send_comuni_geo_text(bot, updates, group=False):
    input_user = updates["text"]
    
    if(group):
        input_user=input_user.split("/luogo")
        input_user=[-1]
    print(input_user)
    check=True
    for comune in data:
        if input_user.lower() == comune["Nome Comune"].lower():
            check=False
            mypos = (comune["Coordinate"]["Latitudine"],comune["Coordinate"]["Longitudine"])
            break

    if(check):
        bot.sendMessage(chat_id=updates["chat"]["id"],text="Errore! inserire un nome di un comune siciliano")
        return
    
    bot.sendLocation(updates["chat"]["id"],mypos[0],mypos[1])
    
    last_positions[updates["chat"]["id"]] = mypos
    print(mypos)
    search_place_near(2000,mypos,bot, updates, False)
    

"""
Funzione che data in input una poszione restituisce o un bottone contenente il comune o i comuni limitrofi.
Se la posizione è al di fuori della Sicilia un messaggio di errore.
"""
def search_place_near(dist_input,mypos,bot, updates, flag):
    nearby_list = list()
    chat = updates["chat"]["id"]
    for comune in data:
        placepos = (comune["Coordinate"]["Latitudine"], comune["Coordinate"]["Longitudine"])
        dist = great_circle(mypos, placepos).meters
        if dist < dist_input:
            nearby_list.append(comune)
    if not nearby_list:
        if(dist_input>125000):
            bot.sendMessage(chat, "Selezionato un comune al di fuori della regione Siciliana")
            return
        search_place_near(dist_input+1000,mypos,bot, updates, True)
    else:
        send_custom_keyboard(bot, updates, nearby_list, flag)

"""
Funzione che invia un messsaggio dall'utente.
"""
def send_custom_keyboard(bot, updates, comune_list,flag):
    text_input = "Seleziona Comune:"
    if(flag):
        text_input="I comuni limitrofi alla posizione selezionata sono:"
    chat = updates["chat"]["id"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='{}'.format(text["Nome Comune"]), callback_data='{}'.format(text["Nome Comune"]))]
                         for text in comune_list])
    bot.sendMessage(chat_id=chat, text=text_input, reply_markup=keyboard)

"""
Funzione per l'estrazione delle imformazioni dal dataset ttl e per la gestione 
dei bottoni relativi e varie informazioni.
"""
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print(query_data)
    comune = query_data.replace(' ','_').replace("'","")
    print(comune)    
    button = comune.split("/")
    option = button[-1]
    city = button[0]
    uri = "<"+URI_BASE_COMUNE+city+">"
    res_musei = ql.info_musei_comune(uri)
    res_musei_rso = ql.info_museirso_comune(uri)
    res_castelli=ql.info_castelli_comune(uri)
    res_beni_imm=ql.info_beni_comune(uri)
    res_luoghi_gusto=ql.info_gusto_comune(uri)
    res_torri=ql.info_torri_comune(uri)

    keyboard = []
    button_option = ["MuseoAll","Museocis","Museorso","Castello","BeneImmateriale","LuogoDelGusto","Torre"]
    check = False
    if option not in button_option:
        if len(res_musei) > 0 and len(res_musei_rso) > 0:
            check = True
            print("Musei trovati")
            keyboard.append(InlineKeyboardButton(text="Musei", callback_data=comune + '/MuseoAll'))
        elif len(res_musei) > 0 :
            check = True
            print("Musei trovati")
            keyboard.append(InlineKeyboardButton(text="Musei", callback_data=comune + '/Museocis'))
        elif len(res_musei_rso) > 0:
            check = True
            print("Musei trovati")
            keyboard.append(InlineKeyboardButton(text="Musei", callback_data=comune + '/Museorso'))
        if len(res_castelli) > 0:
            check = True
            print("Castelli trovati")
            keyboard.append(InlineKeyboardButton(text="Castelli", callback_data=comune + '/Castello'))
        if len(res_beni_imm) > 0:
            check = True
            print("Beni Immateriali trovati")
            keyboard.append(InlineKeyboardButton(text="Beni Immateriali", callback_data=comune + '/BeneImmateriale'))
        if len(res_luoghi_gusto) > 0:
            check = True
            print("Luoghi del gusto trovati")
            keyboard.append(InlineKeyboardButton(text="Luoghi Del Gusto", callback_data=comune + '/LuogoDelGusto'))
        if len(res_torri) > 0:
            check = True
            print("Torri trovate")
            keyboard.append(InlineKeyboardButton(text="Torri", callback_data=comune + '/Torre'))
        if check:
            bot.sendMessage(from_id,text="Informazioni trovate",reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]))
            last_keybords[from_id] = keyboard
        else:
            bot.sendMessage(from_id,text="Ci spiace, nessuna particolarità trovata nelle vicinanze!")
    else:
        if option == "MuseoAll":
            text = ""
            for museo in res_musei:
                nome = "Nome: " + museo[0] + "\n"
                tipo = "Tipo: " + museo[1] + "\n"
                description = "Descrizione: " + museo[4] + "\n"
                text = nome+tipo+description
                bot.sendMessage(from_id,text=text)
                bot.sendLocation(from_id,museo[2],museo[3])
            text = ""
            for museorso in res_musei_rso:
                nome = "Nome: " + museorso[0] + "\n"
                tipo = "Tipo: " + museorso[1] + "\n"
                text = nome+tipo
                
                print("Museorso:",museorso[0])
                try:
                    location = geolocator.geocode(museorso[0])
                    bot.sendLocation(from_id,location.latitude,location.longitude)
                except:
                    text+="\nInformazione sulla geocalizzazione mancante"

                bot.sendMessage(from_id,text=text)

        if option == "Museocis":
            text = ""
            for museo in res_musei:
                nome = "Nome: " + museo[0] + "\n"
                tipo = "Tipo: " + museo[1] + "\n"
                description = "Descrizione: " + museo[4] + "\n"
                text = nome+tipo+description
                if(len(text)>MAX_TEXT):
                    diff = len(text) - MAX_TEXT
                    print("diff", diff)
                    bot.sendMessage(from_id,text=text[:MAX_TEXT])
                    bot.sendMessage(from_id,text=text[MAX_TEXT:])
                else:   
                    bot.sendMessage(from_id,text=text)
                
                bot.sendLocation(from_id,museo[2],museo[3])
            
            
        if option == "Museorso":
            text = ""
            for museorso in res_musei_rso:
                nome = "Nome: " + museorso[0] + "\n"
                tipo = "Tipo: " + museorso[1] + "\n"
                text = nome+tipo
                
                print("Museorso:",museorso[0])
                try:
                    location = geolocator.geocode(museorso[0])
                    bot.sendLocation(from_id,location.latitude,location.longitude)
                except:
                    
                    text+="\nInformazione sulla geocalizzazione mancante"
                bot.sendMessage(from_id,text=text)
        
        if option == "Castello":
            text = ""
            for castello in res_castelli:
                nome = "Nome: " + castello[0] + "\n"
                comment = "Commento: " + castello[1] + "\n"
                date = "Data: " + castello[2] + "\n"
                link = "Link: " + castello[5] + "\n"
                text = nome+comment+date+link
                bot.sendMessage(from_id,text=text)
                bot.sendLocation(from_id,castello[3],castello[4])
            

        if option == "BeneImmateriale":
            text = ""
            for beni in res_beni_imm:
                text += "\""+beni[0]+"\"" + " - " + beni[1] + " - " + beni[2] + "\n"
            bot.sendMessage(from_id,text=text)
            

        if option == "LuogoDelGusto":
            text = ""
            for gusto in res_luoghi_gusto:
                text += "\""+gusto[0]+"\"" + " - " + gusto[1] + "\n\n"
            bot.sendMessage(from_id,text=text)
            

        if option == 'Torre':            
            for torre in res_torri:
                text=torre[0] #label
                bot.sendMessage(from_id,text=text)
                bot.sendLocation(from_id,torre[1],torre[2])
            
        bot.sendMessage(from_id,text="Altre informazioni",reply_markup=InlineKeyboardMarkup(inline_keyboard=[last_keybords[from_id]]))        
        
"""
Funzione per la gestione dei messaggi che riceve il bot.
"""
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'location':
        send_comuni_geo(bot, msg)
    else:
        if msg["text"] == "/start":
            bot.sendMessage(chat_id,
                            "Benvenuto!\nInserisci la tua posizione per scoprire luoghi di interesse nelle tue vicinanze.",
                            reply_markup=None)
        elif msg["text"] == "/info":
            bot.sendMessage(chat_id, "Benventuto nel bot alla scoperta della sicilia.\nDevelopment by Calderaro, Scordato", reply_markup=None)
        elif msg['text'] == "/command":
            bot.sendMessage(chat_id, "\nComandi disponibili: \n /start \n /info \n /command \nOppure inserisci la tua posizione o scrivi un comune siciliano.", reply_markup=None)
        else:
            send_comuni_geo_text(bot,msg)

TOKEN = 'YOUR TOKEN'
bot = telepot.Bot(TOKEN)
data = read_dataset()
last_positions = {}

"""
Funzione Main
"""
def main():
    MessageLoop(bot, {'chat': handle,'callback_query': on_callback_query}).run_as_thread()
    print("In attesa di un messaggio..")
    while 1:
        time.sleep(1)

if __name__ == '__main__':
    main()
