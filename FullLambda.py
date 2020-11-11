#Needed permissions:
# Bucket Access
# Polly Full Acess
# Translate Access


import json
import boto3
import codecs

def lambda_handler(event, context):
    #Translate
    
    translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
    
    translate_result = translate.translate_text(Text="Hello, World. This is a test of the translate service", 
                SourceLanguageCode="en", TargetLanguageCode="es")   
               
    #Polly
    
    from boto3 import Session
    from boto3 import resource

    session = Session(region_name="us-east-1")
    polly = session.client("polly")
    
    s3 = resource('s3')
    bucket_name = "da-proyecto" # Bucket name
    bucket = s3.Bucket(bucket_name)
    
    filename = "mynameis.mp3"
    myText = translate_result.get('TranslatedText')   
    
    response = polly.synthesize_speech(
        Text=myText,
        OutputFormat="mp3",
        VoiceId="Matthew")
        
    stream = response["AudioStream"]
    
    bucket.put_object(Key=filename, Body=stream.read())
