import telebot
from youtubesearchpython import VideosSearch

TOKEN_API = "6636899150:AAH__sSBo1QSwsJe3-3EHEt9X3inlfE_tuA"

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