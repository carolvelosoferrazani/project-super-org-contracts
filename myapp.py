#importanto flask para a aplicação
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from flask import Flask, render_template, url_for, redirect, sessions
import keyboard

app = Flask(__name__)

#escopos de autorização da people api
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

#pagina de login
@app.route('/')
def index():
    return render_template('index.html')

#autenticação
@app.route('/home')
def authorize():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server(port=0)
            #(!)gambiarra para fechar a pagina 
            keyboard.press_and_release('ctrl+w')
         #Salva as credenciais JSON
        #with open('token.json', 'w') as token:
            #token.write(creds.to_json())

    service = build('people', 'v1', credentials=creds)

    # Obtendo os emails da people api
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=100,
        personFields='names,emailAddresses').execute()
    connections = results.get('connections', [])
    for person in connections:
        emails= person.get('emailAddresses', [])
        if emails:
            email = emails[0].get('value')
    dominios = []
    meusEmails = []
    contador = 0
    emailString = ""
    listaEmails = []
    emails = []
    emails.append(email)
    #filtrando os dominios
    for contatos in emails:
        if contatos.split('@')[1] not in dominios:
            dominios.append(contatos.split('@')[1])
            meusEmails.append([])
    for domain in dominios:
        contador+=1
        for email in emails:
            if email.split('@')[1] == dominios[contador-1]:
                meusEmails[contador -1].append(email)
    #filtrando os emails
    for domain in meusEmails:
        emailString = ""
        for c in range(len(domain)):
            if c == len(domain)-1:
                emailString += domain[c]
                break
            emailString += domain[c] + " / "
        listaEmails.append(emailString)
        
    return render_template('home.html', dominios=dominios, meusEmails=meusEmails, listaEmails=listaEmails)

if __name__ == "__main__":
    app.run(debug=True)
