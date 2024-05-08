from all_imports import *

load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_API = os.getenv('BOT_TOKEN')

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

@assistbot.message_handler(commands=['help', 'ajuda'])
def instrucoes(mensagem):
   
    assistbot.reply_to(mensagem, "\n Olá, eu sou o robô assistente AssitBot. \n \n Atualmente, eu tenho os seguintes comandos:\n\n" \
                       "/help ou /ajuda: ver os comandos disponíveis \n"\
                       "/youtube ou /yt <o que deseja pesquisar>: pesquisar algum vídeo no youtube \n"\
                       "/calendario: ver calendários existentes no Google Agenda \n"\
                       "/eventos: ver eventos existentes no Google Agenda \n"\
                       "/novo_evento <nome do evento>  <data de início> <hora de início> <data fim> <horário fim> <emails para convidar separados por espaço>")


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


# Se retornar True, vai acionar o bot via @assistbot.message_handler().
# É com essa função que vamos decidir quais tipos de mensagem serão respondidas pelo bot.
#def verificar(mensagem):
#    return True

#@assistbot.message_handler(func=verificar)
#def responder(mensagem):
#    assistbot.reply_to(mensagem, "Agora eu consigo responder a qualquer mensagem que vc mandar com esse mesmo texto. Mas para isso, é necessário deixar o código rodando em algum pc.")

# Se alguém mandar alguma mensagem enquanto o código não estiver rodando, essa pessoa só será respondida se o
# código voltar a rodar em algum pc.

def main(): 
    assistbot.infinity_polling()

if __name__ == "__main__":
    main()
