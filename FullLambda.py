# Needed permissions:
# Bucket Access
# Polly Full Acess
# Translate Access


import json
import boto3
import codecs
from boto3 import Session
from boto3 import resource


def lambda_handler(event, context):

    # API variables
    source_languaje_code = "en"  # arb,cmn,da,nl,en,es,fr, de etc
    target_languaje_code = "es"
    transcribe_text = "Hello, World. This is a test of the translate service"

    # Translate
    translate = boto3.client(service_name='translate',
                             region_name='us-east-1', use_ssl=True)

    translate_result = translate.translate_text(Text=transcribe_text,
                                                SourceLanguageCode=source_languaje_code, TargetLanguageCode=target_languaje_code)

    # Polly
    session = Session(region_name="us-east-1")
    polly = session.client("polly")

    s3 = resource('s3')
    bucket_name = "da-proyecto"  # Nombre del bucket
    bucket = s3.Bucket(bucket_name)

    filename = source_languaje_code.upper() + "_AudioTo_" + \
        target_languaje_code.upper() + ".mp3"
    translated_text = translate_result.get('TranslatedText')

    # Select appropriate voice for the output language
    choices = {'en': 'Joanna', 'es': 'Miguel'}
    voice_id = choices.get(target_languaje_code, 'es')

    response = polly.synthesize_speech(
        Text=translated_text,
        OutputFormat="mp3",
        VoiceId=voice_id)

    stream = response["AudioStream"]

    bucket.put_object(Key=filename, Body=stream.read())
