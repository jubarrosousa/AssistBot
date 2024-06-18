import os.path
import pickle
import datetime as dt
import threading
import time
import json
import requests
import urllib.parse
import base64
from flask import Flask, redirect, request, jsonify, session
import logging
import json


app = Flask(__name__)
app.secret_key = 'kjasbddfjksbf23425'

CLIENT_ID = '0876a55370cf4010a08f6404211039ac'
CLIENT_SECRET = 'c43a2f64fb3e4377bca3a5dc54e0fb8c'
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'playlist-modify-public playlist-modify-private'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/' 

@app.route('/')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    app.logger.warning('entering callback')
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = dt.datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    app.logger.warning('entering get_playlist')
    if 'access_token' not in session:
        return redirect('/')

    if dt.datetime.now().timestamp() > session['expires_at']:
        app.logger.warning('entering refresh-token')
        return redirect('/refresh-token')

    header = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + 'me/playlists', headers = header)
    playlists = response.json()

    return jsonify(playlists)

@app.route('/refresh_token')
def refresh_token():
    app.logger.warning('entering refresh_token')
    if 'refresh_token' not in session:
        return redirect('/')
    
    if dt.datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_code',
            'refresh_code': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = dt.datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')
    


if __name__ == '__main__':

    app.run()