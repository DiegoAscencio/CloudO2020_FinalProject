#Needed permissions:
# Bucket Access
# Polly Full Acess

import json
import boto3
import codecs

def lambda_handler(event, context):
    from boto3 import Session
    from boto3 import resource

    session = Session(region_name="us-east-1")
    polly = session.client("polly")
    
    s3 = resource('s3')
    bucket_name = "da-proyecto" # Nombre del bucket
    bucket = s3.Bucket(bucket_name)
    
    filename = "mynameis.mp3"
    myText = """
    Hello,
    My name is Diego.
    This is my first Test
    """
    
    response = polly.synthesize_speech(
        Text=myText,
        OutputFormat="mp3",
        VoiceId="Matthew")
        
    stream = response["AudioStream"]
    
    bucket.put_object(Key=filename, Body=stream.read())
