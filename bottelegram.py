import telebot
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os.path
import pickle
import datetime
import schedule 
import threading
import time
import json
import requests
import requests
import urllib.parse
import base64
from flask import Flask, redirect, request, jsonify, session
import urllib.parse
import re


SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_API = "6636899150:AAH__sSBo1QSwsJe3-3EHEt9X3inlfE_tuA"
CHAT_ID = "-1002056949053"

CLIENT_ID = '0876a55370cf4010a08f6404211039ac'
CLIENT_SECRET = 'c43a2f64fb3e4377bca3a5dc54e0fb8c'
REDIRECT_URI = 'http://localhost:5000/callback'
#REDIRECT_URI = 'https://ea5c-2804-14d-5c51-8d74-f4e3-c77-f53d-23f0.ngrok-free.app/callback' 
scope = 'playlist-modify-public playlist-modify-private user-read-private user-read-email playlist-read-private playlist-read-collaborative'


AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/' 


# Dicionário de substituição para traduzir os nomes dos dias da semana e dos meses para o português
traducoes = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro"
}

assistbot = telebot.TeleBot(TOKEN_API)

@assistbot.message_handler(commands=['login_spotify'])
def login(message):

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    assistbot.reply_to(message, f"Click the link to login to Spotify: {auth_url}")

@assistbot.message_handler(commands=['playlists'])
def get_playlists(message):

    creds = None
    if os.path.exists('creds.pickle'):
        with open('creds.pickle', 'rb') as token:
            creds = pickle.load(token)
            print(creds)

    if not creds or datetime.datetime.now().timestamp() > creds['expires_at']:
        assistbot.reply_to(message, "Sessao expirada ou nao autenticada. Por favor, use /login_spotify para autenticar novamente.")
        return
    
    header = {
        'Authorization': f"Bearer {creds['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=header)

    playlists = response.json()

    if 'items' in playlists:
        playlist_names = [playlist['name'] for playlist in playlists['items']]
        assistbot.reply_to(message, "\n".join(playlist_names))
    else:
        assistbot.reply_to(message, "Falha ao recuperar as playlists.")

@assistbot.message_handler(commands=['criar_playlist'])
def create_playlist(message):

    creds = None
    if os.path.exists('creds.pickle'):
        with open('creds.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or datetime.datetime.now().timestamp() > creds['expires_at']:
        assistbot.reply_to(message, "Sessao expirada ou nao autenticada. Por favor, use /login_spotify para autenticar novamente.")
        return

    headers = {
        'Authorization': f"Bearer {creds['access_token']}",
        'Content-Type': 'application/json'
    }
    user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_info = user_response.json()

    if 'id' in user_info:
        user_id = user_info['id']
        playlist_name = message.text[len('/criar_playlist '):].strip()
        print(playlist_name)

        if not playlist_name:
            assistbot.reply_to(message, "Please provide a playlist name. Usage: /criar_playlist <nome playlist>")
            return
        
        playlist_data = {
            "name": playlist_name,
            #"description": "New playlist created from Telegram bot",
            "public": False
        }
        response = requests.post(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=headers, json=playlist_data)
        playlist_info = response.json()
        print(playlist_info)
        
        if 'id' in playlist_info:
            assistbot.reply_to(message, f"Playlist '{playlist_name}' criada com sucesso!")
        else:
            assistbot.reply_to(message, "Falha ao criar playlist.")
    else:
        assistbot.reply_to(message, "Falha ao recuperar as informacoes do usuario.")

@assistbot.message_handler(commands=['adicionar_musica'])
def adicionar_musica(message):
    creds = None
    if os.path.exists('creds.pickle'):
        with open('creds.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or datetime.datetime.now().timestamp() > creds['expires_at']:
        assistbot.reply_to(message, "Sessao expirada ou nao autenticada. Por favor, use /login_spotify para autenticar novamente.")
        return

    headers = {
        'Authorization': f"Bearer {creds['access_token']}",
        'Content-Type': 'application/json'
    }

    try:
        command_text = message.text[len('/adicionar_musica '):].strip()
        matches = re.findall(r'"([^"]*)"', command_text)
        playlist_name, song_name = matches
        

    except:
        assistbot.reply_to(message, "Insira um comando válido. Uso: /adicionar_musica \"nome playlist\" \"nome musica\"")
        return

    headers = {
        'Authorization': f"Bearer {creds['access_token']}",
        'Content-Type': 'application/json'
    }

    if not playlist_name:
        assistbot.reply_to(message, "Por favor, informe o nome de uma playlist. Uso: /adicionar_musica \"nome playlist\" \"nome musica\"")
        return

    user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_info = user_response.json()

    if 'id' in user_info:
        user_id = user_info['id']
        playlists_response = requests.get(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=headers)
        playlists_info = playlists_response.json()

        if 'items' in playlists_info:

            encontrou = False
            for playlist in playlists_info['items']:
                if playlist['name'].lower() == playlist_name.lower():
                    playlist_id = playlist['id']
                    encontrou = True
                    break
                    #assistbot.reply_to(message, f"Playlist '{playlist_name}' ID: {playlist['id']}")

            if encontrou == False:
                assistbot.reply_to(message, f"Nenhuma playlist encontrada com esse nome.'{playlist_name}'.")
        else:
            assistbot.reply_to(message, f"Falha ao recuperar as playlists. Erro: {playlists_info}")
    else:
        assistbot.reply_to(message, f"Falha ao recuperar as informacoes do usuario. Erro: {user_info}")

    search_params = {
        'q': song_name,
        'type': 'track',
        'limit': 1
    }
    search_response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=search_params)
    search_results = search_response.json()

    if search_results['tracks']['items']:
        track_uri = search_results['tracks']['items'][0]['uri']
        add_track_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        add_track_response = requests.post(add_track_url, headers=headers, json={'uris': [track_uri]})
        
        if add_track_response.status_code == 200:
            assistbot.reply_to(message, f"Música '{song_name}' adicionada com sucesso a playlist!")
        else:
            assistbot.reply_to(message, f"Falha ao adicionar a música na playlist. Error: {add_track_response.json()['error']['message']}")
    else:
        assistbot.reply_to(message, "Nenhum resultado encontrado para essa musica.")

@assistbot.message_handler(commands=['musicas_playlist'])
def musicas_playlist(message):
    creds = None
    if os.path.exists('creds.pickle'):
        with open('creds.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or datetime.datetime.now().timestamp() > creds['expires_at']:
        assistbot.reply_to(message, "Sessao expirada ou nao autenticada. Por favor, use /login_spotify para autenticar novamente.")
        return

    headers = {
        'Authorization': f"Bearer {creds['access_token']}",
        'Content-Type': 'application/json'
    }
    try:
        command_text = message.text[len('/musicas_playlist '):].strip()

    except:
        assistbot.reply_to(message, "Insira um comando válido. Uso: /musicas_playlist nome playlist")
        return


    user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_info = user_response.json()

    if 'id' in user_info:
        user_id = user_info['id']
        playlists_response = requests.get(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=headers)
        playlists_info = playlists_response.json()

        playlist_id = None
        if 'items' in playlists_info:
            for playlist in playlists_info['items']:
                if playlist['name'].lower() == command_text.lower():
                    playlist_id = playlist['id']
                    break

        if playlist_id:
            playlist_tracks_response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers)
            playlist_tracks_info = playlist_tracks_response.json()

            if 'items' in playlist_tracks_info:
                songs_list = []
                for track in playlist_tracks_info['items']:
                    track_name = track['track']['name']
                    artist_name = track['track']['artists'][0]['name']
                    songs_list.append(f"{track_name} - {artist_name}")

                assistbot.reply_to(message, f"Playlist '{command_text}' musicas:\n\n" + "\n".join(songs_list))
            else:
                assistbot.reply_to(message, f"Nenhuma música foi encontrada nessa playlist '{command_text}'.")
        else:
            assistbot.reply_to(message, f"Nenhuma playlist encontrada com esse nome.'{command_text}'.")
    else:
        assistbot.reply_to(message, f"Falha ao recuperar as informacoes do usuario. Error: {user_info}")

@assistbot.message_handler(commands=['help', 'ajuda'])
def instrucoes(mensagem):
   
    assistbot.reply_to(mensagem, "\n Olá, eu sou o robô assistente AssitBot. \n \n Atualmente, eu tenho os seguintes comandos:\n\n" \
                       "/help ou /ajuda: ver os comandos disponíveis \n"\
                       "/youtube ou /yt <o que deseja pesquisar>: pesquisar algum vídeo no youtube \n"\
                       "/calendario: ver calendários existentes no Google Agenda \n"\
                       "/eventos: ver eventos existentes no Google Agenda \n"\
                       "/novo_evento <nome do evento>  <data de início> <hora de início> <data fim> <horário fim> <emails para convidar separados por espaço> \n"\
                       "/deletar <nome do evento que deseja deletar> \n"\
                       "/login_spotify: permite os comandos associados à conta spotify do bot \n"\
                       "/playlists: lista as playlists do bot no spotify \n"\
                       "/criar_playlist <nome da playlist que será criada na conta do bot> \n"\
                       "/adicionar_musica \"nome da playlist\" \"nome da música\"")

@assistbot.message_handler(commands=['chat_id'])
def send_chat_id(mensagem):
     assistbot.reply_to(mensagem, mensagem.chat.id)  # This will print the chat ID to the console

@assistbot.message_handler(commands=['auxiliar'])
def send_message_event(mensagem = False):
    print ("Me executaram")
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        servico = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            servico.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        eventos = events_result.get("items", [])

        if not eventos:
            assistbot.send_message(CHAT_ID, "Nenhum evento futuro")
            return
        # Prints the start and name of the next 10 events
        for event in eventos:
            start = event["start"].get("dateTime", event["start"].get("date"))
            
            # Colocando em formato para operacao da datetime e recuperando informacao de agora
            dia_evento = datetime.datetime.strptime(start[:-6], "%Y-%m-%dT%H:%M:%S")
            agora  = datetime.datetime.now()

            # Verificando quanto tempo falta para o evento

            diferenca_de_tempo = dia_evento - agora

            # Se faltar menos de 7 dias começar a enviar alertas
            if (diferenca_de_tempo.days < 7):
                assistbot.send_message(CHAT_ID, f"O evento {event['summary']} se aproxima!\n Ele ocorre em {diferenca_de_tempo.days} dias e {diferenca_de_tempo.seconds // 3600} horas")
                assistbot.send_message(CHAT_ID, f"Link do evento na agenda: {event['htmlLink']}")

    except HttpError as error:
        assistbot.send_message(CHAT_ID, f"Ocorreu um erro: {error}")  

@assistbot.message_handler(commands=['youtube', 'yt'])
def send_video(mensagem):
    texto = mensagem.text
    conteudo = texto.split()

    if len(conteudo) == 1:
        assistbot.reply_to(mensagem, "Uso: /youtube ou /yt <o que deseja pesquisar>")
    else:
        query = ' '.join(conteudo[1:])
        videosSearch = VideosSearch(query, limit = 1)
        assistbot.reply_to(mensagem, (videosSearch.result())['result'][0]['link'])

@assistbot.message_handler(commands=['calendario'])
def verificar_calendarios(mensagem):
    
    texto = mensagem.text
    conteudo = texto.split()
    # print(os.listdir())

    assistbot.reply_to(mensagem, "Recuperando informacoes dos calendarios existentes")

    # Recuperando informacao dos calendarios existentes
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    servico = build('calendar', 'v3', credentials=creds)
    calendar_list = servico.calendarList().list().execute()

    # for calendar in calendar_list['items']:
    #     print(calendar)

    # Feature 1: Listar todos os calendarios
    print("Recuperando informacao dos calendarios:")
    lista_calendario = servico.calendarList().list().execute().get('items', [])
    for calendario in lista_calendario:
        assistbot.reply_to(mensagem, (calendario['summary']))

@assistbot.message_handler(commands=['eventos'])
def verificar_eventos(mensagem):

    texto = mensagem.text
    conteudo = texto.split()
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        servico = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            servico.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        eventos = events_result.get("items", [])

        if not eventos:
            assistbot.reply_to(mensagem, "Nenhum evento futuro")
            return
        # Prints the start and name of the next 10 events
        for event in eventos:
            start = event["start"].get("dateTime", event["start"].get("date"))  
            link = event["htmlLink"]

            inicio = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z").strftime("%A, %B %d, %Y %I:%M %p")

            for nome_en, nome_pt in traducoes.items():
                inicio = inicio.replace(nome_en, nome_pt)

            assistbot.reply_to(mensagem,(f"Inicio : {inicio} \nResumo: {event['summary']} \nLink do evento no calendario: {link}"))

    except HttpError as error:
        assistbot.reply_to(mensagem, f"Ocorreu um erro: {error}")
        
@assistbot.message_handler(commands=['novo_evento'])
def adicionar_eventos(mensagem):
    texto = mensagem.text
    conteudo = texto.split()
    # Conectando com a API
    creds = None

    print(len(conteudo))

    # verificando se tem o número mínimo de argumentos
    if len(conteudo) < 6:
        assistbot.reply_to(mensagem, "Uso: /novo_evento <nome do evento> <data de início> <hora de início>  <data fim> <horário fim> <(opcional) emails para convidar separados por espaço>")
    
    else:

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        try:
            servico = build('calendar', 'v3', credentials=creds)

            participantes = [{'email':'6ano2historia@gmail.com'}]

            print(conteudo)

            data_inicio = str(conteudo[2]) + " " + str(conteudo[3])
            data_fim = str(conteudo[4]) + " " + str(conteudo[5])

            timestamp_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S")
            timestamp_fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")

            data_inicio = timestamp_inicio.strftime("%Y-%m-%dT%H:%M:%S-03:00")
            data_fim = timestamp_fim.strftime("%Y-%m-%dT%H:%M:%S-03:00")

            if (len(conteudo) > 6):
                for i in range (6, len(conteudo)):
                    participantes.append({'email':conteudo[i]})

            event = {
                'summary': conteudo[1],
                'start': {
                    'dateTime': data_inicio,
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': data_fim,
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': participantes
                # 'recurrence': [
                #     'RRULE:FREQ=DAILY;COUNT=2'
                # ]                 
            }


            event = servico.events().insert(calendarId='primary', body=event).execute()
            assistbot.reply_to(mensagem, 'Evento criado: %s' % (event.get('htmlLink')))


        except HttpError as error:
            assistbot.reply_to(mensagem, f"Ocorreu um erro: {error}")

        except ValueError as error:
            assistbot.reply_to(mensagem, f"Ocorreu um erro: {error}")


@assistbot.message_handler(commands=['deletar'])
def deletar_eventos(mensagem):

    encontrou = False
    texto = mensagem.text
    conteudo = texto.split()

    if len(conteudo) == 1:
        assistbot.reply_to(mensagem, "Uso: /deletar <nome do evento>")
    else:
        nome_evento = ' '.join(conteudo[1:])
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        servico = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            servico.events()
            .list(
                calendarId="primary",
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        eventos = events_result.get("items", [])

        if not eventos:
            assistbot.reply_to(mensagem, "Nenhum evento futuro")
            return
        # Verifica se existe um eventocom o nome desejado e pega seu id
        for evento in eventos:

            if(evento['summary'] == nome_evento):
                id_evento = evento['id']
                encontrou = True

        if (encontrou == True):
            # Tenta deletar o evento
            try:
                servico.events().delete(calendarId="primary", eventId=id_evento).execute() 
                assistbot.reply_to(mensagem, f"O evento {nome_evento} foi deletado")
            except Exception as e:
                assistbot.reply_to(mensagem,f"Um erro ocorreu: {e}")

        else:
            assistbot.reply_to(mensagem,(f"Nenhum evento com esse nome foi encontrado"))

    except HttpError as error:
        assistbot.reply_to(mensagem, f"Ocorreu um erro: {error}")

# Se retornar True, vai acionar o bot via @assistbot.message_handler().
# É com essa função que vamos decidir quais tipos de mensagem serão respondidas pelo bot.
#def verificar(mensagem):
#    return True

#@assistbot.message_handler(func=verificar)
#def responder(mensagem):
#    assistbot.reply_to(mensagem, "Agora eu consigo responder a qualquer mensagem que vc mandar com esse mesmo texto. Mas para isso, é necessário deixar o código rodando em algum pc.")

# Se alguém mandar alguma mensagem enquanto o código não estiver rodando, essa pessoa só será respondida se o
# código voltar a rodar em algum pc.

# Funcar para lidar com o envio de mensagens de eventos proximos
def scheduling_thread():
    while True:
        print ("Antes")
        schedule.run_pending()
        print ("Depois")
        time.sleep(60)


def polling_thread():
    while True:
        try:
            assistbot.infinity_polling()
        except Exception as e:
            print(f"Exception in polling thread: {e}")
            time.sleep(5)  # Wait for a while before retrying


# Criar o trigger de envio de mensagens de evento
schedule.every(10).minutes.do(send_message_event)

def main(): 
    assistbot.infinity_polling()

if __name__ == "__main__":
    polling_thread = threading.Thread(target=polling_thread)
    scheduling_thread = threading.Thread(target=scheduling_thread)
    
    polling_thread.start()
    scheduling_thread.start()
