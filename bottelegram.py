import telebot

TOKEN_API = "6636899150:AAH__sSBo1QSwsJe3-3EHEt9X3inlfE_tuA"

assistbot = telebot.TeleBot(TOKEN_API)

# Se retornar True, vai acionar o bot via @assistbot.message_handler().
# É com essa função que vamos decidir quais tipos de mensagem serão respondidas pelo bot.
def verificar(mensagem):
    return True

@assistbot.message_handler(func=verificar)

def responder(mensagem):
    assistbot.reply_to(mensagem, "Agora eu consigo responder a qualquer mensagem que vc mandar com esse mesmo texto. Mas para isso, é necessário deixar o código rodando em algum pc.")

# Se alguém mandar alguma mensagem enquanto o código não estiver rodando, essa pessoa só será respondida se o
# código voltar a rodar em algum pc.

assistbot.polling()