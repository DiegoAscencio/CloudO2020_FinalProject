import boto3
from botocore.config import Config
import json
import random
import time
from urllib.request import urlopen
from flask import Flask, render_template, g, make_response, redirect, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def create_obj():
    ###################### REQUEST VALIDATIONS ######################
    # File
    if 'audio' not in request.files:
        return "No audio file in POST"
    # Languages
    if 'sourceLanguage' not in request.form or 'destinationLanguage' not in request.form:
        return 'Define languages in request'

    ###################### GENERAL INFORMATION ######################
    # Languages
    sourceLanguage = request.form.get('sourceLanguage')
    destinationLanguage = request.form.get('destinationLanguage')
    languageChoices = {
        'en': 'Joanna', 
        'es': 'Miguel'
    }
    voiceId = languageChoices.get(destinationLanguage, 'es')
    # Random number to differentiate file
    randomNumber = str(int(random.random() * 10000))
    inputAudioName = 'inputAudio' + randomNumber + '.mp3'
    outputAudioName = 'outputAudio' + randomNumber + '.mp3'
    # AWS info
    awsClientConfig = Config(region_name = 'us-east-1')
    bucket_name = 'cloudproject-translator-bucket'
    # Data from process
    transcribedText = ''
    translatedText = ''
    # Response
    response = {}
    response['bucket'] = bucket_name
    response['sourceLanguage'] = sourceLanguage
    response['destinationLanguage'] = destinationLanguage
    response['inputAudio'] = inputAudioName
    response['outputAudio'] = outputAudioName
    
    ############################# UPLOAD AUDIO TO S3 ##############################
    print('Uploading audio to S3...')
    # Get resource
    s3 = boto3.resource('s3')
    # Create object
    object = s3.Object(bucket_name, inputAudioName)
    # Get audio and save it in S3
    inputAudioData = request.files['audio'].read()
    object.put(Body = inputAudioData)
    object.wait_until_exists()
    print('DONE')

    ############################# TRANSCRIBE AUDIO ################################
    print('Transcribing audio...')
    # Get client
    transcribe = boto3.client('transcribe', config = awsClientConfig)
    # Define job
    job_name = 'transcriptionJob' + randomNumber
    job_uri = 'https://s3.amazonaws.com/' + bucket_name + '/' + inputAudioName

    # Start transcription
    transcribe.start_transcription_job(
        TranscriptionJobName = job_name, 
        Media = {'MediaFileUri': job_uri}, 
        MediaFormat = 'mp3', 
        LanguageCode = sourceLanguage
    )

    # Wait for the transcription job (Waiters are not provided by the SDK)
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("\tTranscription not ready yet...")
        time.sleep(5)
    
    # Transcription job completed
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcriptFileUri = urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        data = json.loads(transcriptFileUri.read())
        transcribedText = data['results']['transcripts'][0]['transcript']

        response['inputText'] = transcribedText

        print('DONE')
    else:
        response['error'] = 'Error in transcription'
        return response

    ############################# TRANSLATE TEXT ##################################
    print('Translating text...')
    # Get client
    translate = boto3.client(service_name='translate', config=awsClientConfig)
    # Start translation
    translationResult = translate.translate_text(
        Text = transcribedText, 
        SourceLanguageCode = sourceLanguage[0:2], 
        TargetLanguageCode = destinationLanguage
    )

    translatedText = translationResult.get('TranslatedText')
    response['translatedText'] = translatedText
    print('DONE')

    ############################# TEXT TO VOICE ####################################
    print('Converting text to voice...')
    # Get client
    polly = boto3.client('polly', config = awsClientConfig)
    # Start conversion
    pollyTask = polly.synthesize_speech(
        Text = translatedText,
        OutputFormat = 'mp3',
        VoiceId = voiceId
    )
    # Read new audio
    outputAudioData = pollyTask["AudioStream"].read()
    # Save audio in S3
    object = s3.Object(bucket_name, outputAudioName)
    object.put(Body = outputAudioData)
    object.wait_until_exists()
    print('DONE')

    return response

if(__name__ == '__main__'):
    app.run(host='0.0.0.0', port=3000, debug=True)
