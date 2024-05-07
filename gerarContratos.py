from docx import Document
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define as credenciais do Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\Felipe\\credentials.json', scope)


localArquivoExcel = 'G:\\Meu Drive\\00 Música\\casamentos\\Contratos\\Serviço de música para cerimônias (respostas).gsheet'

localArquivoTxt = "G:\\Meu Drive\\00 Música\\casamentos\\Contratos\\ultimaAtualizacaoDoArquivoExcel.txt"

def get_last_modified_time(file_path):
    # Retorna o tempo de modificação do arquivo em segundos desde a época (UNIX timestamp)
    timestamp = os.path.getmtime(file_path)
    # Converter o timestamp para um objeto de tempo (pode ser convertido para diferentes formatos)
    last_modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    return last_modified_time

def salvar_arquivo_txt(conteudo):
    with open(localArquivoTxt, "w") as arquivo:
        arquivo.write(conteudo)

def atualizou_excel(ultimaAtualizacaoDoArquivoExcel):
    with open(localArquivoTxt, 'r') as arquivo:
        ultimaAtualizacaoVerificada = arquivo.read()

        if ultimaAtualizacaoVerificada == ultimaAtualizacaoDoArquivoExcel:
            return False
        else:
            return True
"""
def substituir_texto(doc, antigo, novo):
    for paragrafo in doc.paragraphs:
        for run in paragrafo.runs:
            texto = run.text.replace(antigo, novo)
            run.text = texto
"""

ultimaAtualizacaoDoArquivoExcel = get_last_modified_time(localArquivoExcel)

if atualizou_excel(ultimaAtualizacaoDoArquivoExcel):
    # Vamos encontrar a(s) nova(s) linha(s) adicionada(s) e 1) cadastrar evento no bot; 2) criar o(s) contrato(s).
    # Vamos nomear os novos contratos na fórmula AAAAMMDD{CPF do primeiro contratante}, assim poderemos varrer as linhas de baixo para cima, e saber se o contrato referente àquela linha já foi escrito ou não (caso mais de uma linha tenha sido criada enquanto o bot estivesse desligado).
    
    # Autoriza e abre a planilha
    client = gspread.authorize(credentials)
    planilha = client.open('Serviço de música para cerimônias (respostas)')
    pagina = planilha.sheet1

    # Obtém os dados da planilha
    dados = pagina.get_all_records()
    print(dados)
    salvar_arquivo_txt(ultimaAtualizacaoDoArquivoExcel)

else:
    pass

print("Hora da última modificação:", ultimaAtualizacaoDoArquivoExcel)


"""
# Abrir o arquivo Word
documento = Document('seu_arquivo.docx')

# Definir os caracteres antigos e novos
caracteres_antigos = 'caracteres antigos'
caracteres_novos = 'caracteres novos'

# Substituir os caracteres no documento
substituir_texto(documento, caracteres_antigos, caracteres_novos)

# Salvar o documento modificado
documento.save('arquivo_modificado.docx')
"""