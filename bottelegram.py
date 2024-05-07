import telebot
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os.path
import pickle
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_API = "6636899150:AAH__sSBo1QSwsJe3-3EHEt9X3inlfE_tuA"

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
def verificar_eventos(mensagem):
    
    texto = mensagem.text
    conteudo = texto.split()
    # print(os.listdir())

    if (len(conteudo) == 1):
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

        # Feature 1: Listar todos os calendarios
        print("Recuperando informacao dos calendarios:")
        lista_calendario = servico.calendarList().list().execute().get('items', [])
        for calendario in lista_calendario:
            assistbot.reply_to(mensagem, (calendario['summary']))

    elif(conteudo[1] == 'eventos'):

        # Conectando com a API
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
        
    elif (conteudo[1] == 'adicionar'):
        # Conectando com a API
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

            print(conteudo)

            data_inicio = str(conteudo[3]) + " " + str(conteudo[4])
            data_fim = str(conteudo[5]) + " " + str(conteudo[6])

            timestamp_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S")
            timestamp_fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")

            data_inicio = timestamp_inicio.strftime("%Y-%m-%dT%H:%M:%S-03:00")
            data_fim = timestamp_fim.strftime("%Y-%m-%dT%H:%M:%S-03:00")

            event = {
                'summary': conteudo[2],
                'start': {
                    'dateTime': data_inicio,
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': data_fim,
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': [
                    {'email': '6anohistoria@gmail.com'},
                    {'email': 'filipebf852@poli.ufrj.br'},
  ]
                # 'recurrence': [
                #     'RRULE:FREQ=DAILY;COUNT=2'
                # ]                 
            }

            event = servico.events().insert(calendarId='primary', body=event).execute()
            assistbot.reply_to(mensagem, 'Evento criado: %s' % (event.get('htmlLink')))

        except HttpError as error:
            assistbot.reply_to(mensagem, f"Ocorreu um erro: {error}")

# Se retornar True, vai acionar o bot via @assistbot.message_handler().
# É com essa função que vamos decidir quais tipos de mensagem serão respondidas pelo bot.
def verificar(mensagem):
    return True

@assistbot.message_handler(func=verificar)
def responder(mensagem):
    assistbot.reply_to(mensagem, "Agora eu consigo responder a qualquer mensagem que vc mandar com esse mesmo texto. Mas para isso, é necessário deixar o código rodando em algum pc.")

# Se alguém mandar alguma mensagem enquanto o código não estiver rodando, essa pessoa só será respondida se o
# código voltar a rodar em algum pc.

def main(): 
    assistbot.infinity_polling()

if __name__ == "__main__":
    main()
