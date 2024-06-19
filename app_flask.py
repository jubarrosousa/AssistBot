from flask import Flask, request, redirect
import requests
import datetime as dt
import json
import pickle

app = Flask(__name__)

CLIENT_ID = '0876a55370cf4010a08f6404211039ac'
CLIENT_SECRET = 'c43a2f64fb3e4377bca3a5dc54e0fb8c'
#REDIRECT_URI = 'https://ea5c-2804-14d-5c51-8d74-f4e3-c77-f53d-23f0.ngrok-free.app/callback'
REDIRECT_URI = 'http://localhost:5000/callback'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

TELEGRAM_BOT_TOKEN = "6636899150:AAH__sSBo1QSwsJe3-3EHEt9X3inlfE_tuA"

CHAT_ID = "-1002056949053"  # Store this dynamically if needed

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'No code provided', 400

    req_body = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()

    if 'access_token' in token_info:
        creds = {
            'access_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'expires_at': dt.datetime.now().timestamp() + token_info['expires_in']
        }

        with open('creds.pickle', 'wb') as token:
            pickle.dump(creds, token)

        # with open('creds.json', 'w') as f:
        #     app.logger.warning('entering creds')
        #     json.dump(token_info, f)

        # Send token information to the Telegram bot
        #send_telegram_message(CHAT_ID, f"Access Token: {access_token}\nRefresh Token: {refresh_token}\nExpires At: {expires_at}")
        
        return 'Authentication successful! You can now return to the bot.', 200
    else:
        return 'Authentication failed', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
