# importe les modules nécessaires pour développer une application Flask avec les fonctionnalités de rendu de templates HTML, la gestion des requêtes, la redirection d'URL et la reconnaissance vocale à l'aide de la bibliothèque SpeechRecognition, ainsi que l'API OpenAI.
from flask import Flask, render_template, request, redirect, url_for
import speech_recognition as sr
import openai
from flask import Flask, render_template, request
#Ces deux lignes importent les bibliothèques nécessaires à la reconnaissance vocale et à l'utilisation de l'API OpenAI.
import speech_recognition as sr
import openai
import os
# importe des modules nécessaires pour l'interaction avec les services Google, notamment l'API Google Forms.
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from google.oauth2 import service_account
from googleapiclient.discovery import build
#parcour le répertoire de travail actuel du programme
os.chdir('C:\\Users\ghizl\\3D Objects\\python_code\\text_mining\\project')
#apikey de chatgpt 
openai.api_key = "sk-$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
#Cette ligne de code crée un objet credentials en utilisant le fichier JSON de la clé d'API fourni, 'apikey.json', et les scopes (scopes) spécifiés.
credentials = service_account.Credentials.from_service_account_file('apikey.json',scopes=['https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/drive'])
# initialise une application Flask, définit le point de départ de l'application et définit une route pour l'URL racine ("/").
app = Flask(__name__)
app.debug = True 
@app.route('/')
#cette fonction est appelée et elle renvoie le rendu du template HTML "index.html" à l'aide de la fonction render_template() de Flask.
def index():
    return render_template('index.html')

#cette route sera utilisée pour recevoir des requêtes POST provenant d'un formulaire ou d'une autre source.
@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    # récupère le fichier audio envoyé avec la requête POST à l'aide de request.files
    audio_file = request.files['audio_file']

    # enregistre le fichier audio dans un emplacement temporaire avec le nom "audio_file.wav
    audio_file.save('audio_file.wav')

    # crée un objet de la classe Recognizer du module speech_recognition qui sera utilisé pour effectuer la reconnaissance vocale.
    r = sr.Recognizer()
    # ouvre le fichier audio en utilisant AudioFile du module speech_recognition et le spécifie comme source audio pour la reconnaissance vocale.
    with sr.AudioFile('audio_file.wav') as source:
        #enregistre l'audio à partir de la source spécifiée.
        audio = r.record(source)

        text = r.recognize_google(audio)

    # supprime le fichier audio temporaire.
    os.remove('audio_file.wav')

    #redirige vers la route "generate_form" avec le texte reconnu comme argument dans l'URL.
    return redirect(url_for('generate_form', text=text))
@app.route('/generate', methods=['POST', 'GET'])
# generate_form() semble être une fonction qui génère un formulaire en fonction d'un texte donné.
def generate_form():
    # Récupère la valeur du paramètre 'text' envoyé à la fonction via une requête.
    text= request.args.get('text')
    print(text)
    #Crée un dictionnaire NEW_FORM qui contient les informations pour créer un nouveau formulaire. Le titre du formulaire est défini à partir du texte fourni.
    NEW_FORM = {
        "info": {
            "title": text,
        }
    }
    # Initialise le service Google Forms à l'aide des informations d'identification fournies.
    service = build('forms', 'v1', credentials=credentials)
    # Initialise le service Google Forms à l'aide des informations d'identification fournies.
    form = service.forms().create(
        body=NEW_FORM 
    ).execute()
    #: Démarre une boucle qui effectue la génération de 10 questions pour le formulaire.
    for i in range(10):

        input_text = "Generate a multiple-choice question about: {}, with the options: A: , B: , C: , D: ".format(text)
        # Appelle l'API d'OpenAI pour générer une réponse à partir de l'entrée fournie.
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=input_text,
            max_tokens=100,
            temperature=0.7,
            n=1,
            stop=None,
        )
        # Récupère la question générée à partir de la réponse de l'API et supprime les espaces inutiles.
        question_quiz = response['choices'][0].text.strip()
        parts = question_quiz.split('\n')
        print("Parts:", parts)
        

        if len(parts) >= 5:
            #Crée un dictionnaire NEW_QUESTION qui contient les informations pour créer une nouvelle question dans le formulaire.
            NEW_QUESTION = {
                "requests": [{
                    "createItem": {
                        "item": {
                            "title": parts[0],
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {"value": parts[1]},
                                            {"value": parts[2]},
                                            {"value": parts[3]},
                                            {"value": parts[4]}
                                        ],
                                        "shuffle": True
                                        }
                                    }
                                },
                            },
                        "location": {
                        "index": 0
                        }
                    }
                }]
            }
            print("NEW_QUESTION:", NEW_QUESTION)
            # Met à jour le formulaire en ajoutant la nouvelle question à l'aide du service Forms.
            question_setting = service.forms().batchUpdate(formId = form['formId'], body = NEW_QUESTION).execute()
            #Récupère les résultats du formulaire pour obtenir le lien du formulaire généré.
            get_result = service.forms().get(formId=form["formId"]).execute()
    # return render_template('index.html', recognized_text=text, form_url=get_result['responderUri'])
    return render_template('index.html', recognized_text=text, form_url=get_result['responderUri'])
#démarre le serveur Flask et met l'application en attente de requêtes entrantes.
if __name__ == '__main__':
    app.run(port='80')