# Permissions: AmazonS3FullAccess, AmazonTranscribeFullAccess

import json
import boto3
import base64
import time
import urllib

def lambda_handler(event, context):
    # Services
    s3 = boto3.resource('s3')
    transcribe = boto3.client('transcribe')
    
    # Variables
    bucket_name = '704205-test-transcribe'
    filename = 'myfile.mp3'
    
    # Prepare object
    object = s3.Object(bucket_name, filename)
    
    print('--------------EVENT--------------')
    print(event)
    print('---------------------------------')
    
    # Get audio and save it on S3
    file = base64.b64decode(event['body'])
    object.put(Body=file)
    object.wait_until_exists()
    
    
    job_name = 'MyTranscriptionJob'
    job_uri = 'https://s3.amazonaws.com/' + bucket_name + '/' + filename
    inputLanguageCode = 'es-ES'
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name, 
        Media={'MediaFileUri': job_uri}, 
        MediaFormat='mp3', 
        LanguageCode=inputLanguageCode
    )
    
    # Wait for the transcription job (Waiters are not provided by the API)
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            Break
        print("Not ready yet...")
        time.sleep(2)
    print(status)
    
    
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = urllib.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        data = json.loads(response.read())
        text = data['results']['transcripts'][0]['transcript']
        print('--------------TRANSCRIPTION--------------')
        print(text)
        print('-----------------------------------------')
    
    
    

    
    return {
        'statusCode': 200,
        'body': json.dumps('Audio en S3')
    }
