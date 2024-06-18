from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

import os.path

# ID e range da planilha google (que pode ser alimentada por um formulário google).
SPREADSHEET_ID = "1iKTMh7IqPUWvc_ocABJbqQ0artwA3kcR_0KdkE95As0"
RANGE_NAME = "Respostas ao formulário 1!A1:AH10"

# O arquivo token.json é atraledo a esse scope: se alterar o scope, precisa alterar o .json
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Identifica o arquivo txt presente neste diretório - usado para controlar as atualizações do formulário.
ARQ = "qtd_respostas_processadas.txt"


def autenticar_e_guardar_planilha():

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      print(os.listdir())
      flow = InstalledAppFlow.from_client_secrets_file(
          "creds_sheet.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    planilha = result.get("values", [])

    if not planilha:
      print("No data found.")
      return
    
    return planilha

  except HttpError as err:
    print(f'Erro ao acessar a planilha: {err}')


def criar_eventos(contrato):
   pass
# event = {
#                 'summary': conteudo[1],
#                 'start': {
#                     'dateTime': data_inicio,
#                     'timeZone': 'America/Sao_Paulo',
#                 },
#                 'end': {
#                     'dateTime': data_fim,
#                     'timeZone': 'America/Sao_Paulo',
#                 },
#                 'attendees': participantes        
#             }

def atualizar_informacoes(arq_qtd_respostas_processadas, planilha):
    # Guarda a quantidade de linhas preenchidas atualmente na planiha
    qtd_respostas = len(planilha)
    
    # Recupera a informação de "quantas respostas já foram processadas"
    with open(arq_qtd_respostas_processadas, 'r') as arquivo:
        qtd_respostas_processadas = int(arquivo.read())

    # O "while" a seguir garante que todas as respostas do formulário sejam processadas uma vez:
    while (qtd_respostas_processadas < qtd_respostas):
        # salva as informações do novo contrato // cadastra evento
        dados_novo_contrato = planilha[qtd_respostas_processadas]
        print(dados_novo_contrato)
        print("\n\n")
        criar_eventos(dados_novo_contrato)

        qtd_respostas_processadas += 1

        # atualiza arquivo txt com a quantidade de respostas processadas
        with open(arq_qtd_respostas_processadas, 'w') as arquivo:
            arquivo.write(str(qtd_respostas_processadas))

    print("As informações estão atualizadas.\n\n")
    return 


def main():

    planilha = autenticar_e_guardar_planilha()
    atualizar_informacoes(ARQ, planilha)


if __name__ == "__main__":
  main()
